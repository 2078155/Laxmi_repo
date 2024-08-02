from __future__ import annotations

from typing import Tuple, Dict, Any
from trulens_eval.feedback import prompts
# from trulens_eval.feedback.provider import AzureOpenAI
from trulens_eval.feedback.provider.litellm import LiteLLM
from typing import Dict, Optional, Sequence
from trulens_eval.utils.imports import OptionalImports
from trulens_eval.utils.imports import REQUIREMENT_LITELLM
import warnings
import re

with OptionalImports(messages=REQUIREMENT_LITELLM):
    import litellm
    from litellm import completion

    from trulens_eval.feedback.provider.endpoint import LiteLLMEndpoint
from trulens_eval.utils.generated import re_0_10_rating
from src.GENAI import CustomPrompts


class CustomLLM(LiteLLM):

    def _create_chat_completion(
        self,
        prompt: Optional[str] = None,
        messages: Optional[Sequence[Dict]] = None,
        **kwargs
    ) -> tuple[Any, object]:

        if prompt is not None:
            comp = completion(
                model=self.model_engine,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                **kwargs
            )
        elif messages is not None:
            comp = completion(
                model=self.model_engine, messages=messages, **kwargs
            )
        else:
            raise ValueError("`prompt` or `messages` must be specified.")
        assert isinstance(comp, object)
        return comp["choices"][0]["message"]["content"], comp

    def generate_score_and_reasons(
        self,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        normalize: float = 10.0
    ) -> tuple[float | Any, dict[Any, Any], object]:
        """
        Generator and extractor for LLM prompts. It will look for
        "Supporting Evidence" template.

        Args:
            system_prompt (str): A pre-formated system prompt

        Returns:
            The score (float): 0-1 scale and reason metadata (dict) if available.
        """
        assert self.endpoint is not None, "Endpoint is not set."

        llm_messages = [{"role": "system", "content": system_prompt}]
        if user_prompt is not None:
            llm_messages.append({"role": "user", "content": user_prompt})

        response,info = self.endpoint.run_in_pace(
            func=self._create_chat_completion, messages=llm_messages
        )
        if "Supporting Evidence" in response:
            score = -1
            supporting_evidence = None
            criteria = None
            lines = response.split('\n')
            supporting_evidence = ""
            for i, line in enumerate(lines):  # Declare i and loop over lines
                if "Score" in line:
                    score = re_0_10_rating(line) / normalize
                if "Criteria" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        criteria = ":".join(parts[1:]).strip()
                if "Supporting Evidence" in line:
                    # Extract text after "Supporting Evidence:" on the same line
                    supporting_evidence = line[
                                          line.index("Supporting Evidence:") + len("Supporting Evidence:"):].strip()
                    # Look for more supporting evidence in the subsequent lines
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        # Skip empty lines
                        if not next_line:
                            i += 1
                            continue
                        # Remove pointer symbol if present
                        if re.match(r'^[\*\-\•]\s?', next_line):
                            supporting_evidence += " " + next_line[1:].strip()  # Exclude the pointer symbol
                        else:
                            supporting_evidence += " " + next_line
                        i += 1  # Move to the next line
                    break  # Break out of the loop once supporting evidence is found or no more lines are lef
                else:
                    supporting_evidence = "No supporting evidence found"
            reasons = {
                'reason':
                    (
                        f"{'Criteria: ' + str(criteria)}\n"
                        f"{'Supporting Evidence: ' + str(supporting_evidence)}"
                    )
            }
            print("Reasons from litellm=============\n\n\n",reasons)
            return score, reasons, info

        else:
            score = re_0_10_rating(response) / normalize
            warnings.warn(
                "No supporting evidence provided. Returning score only.",
                UserWarning
            )
            return score, {}, info

    def _factuality_doc_in_out(self, premise: str, hypothesis: str) -> tuple:
        """
        An LLM prompt using the entire document for premise and entire statement
        document for hypothesis.

        Args:
            premise (str): A source document
            hypothesis (str): A statement to check

        Returns:
            str: An LLM response using a scorecard template
        """
        assert self.endpoint is not None, "Endpoint is not set."

        return self.endpoint.run_in_pace(
            func=self._create_chat_completion,
            prompt=str.format(CustomPrompts.LLM_FACTUALITY_FULL_SYSTEM,
                              premise=premise,
                              hypothesis=hypothesis
                              )
        )

    def factuality_with_cot_reasons(self, context: str, answer: str) -> tuple[dict[str, float], dict[str, str], str]:
        """
        Tweaked version of groundedness, extending AzureOpenAI provider.
        A function that completes a template to check the factuality of the statement to the question.
        Also uses chain of thought methodology and emits the reasons.

        Args:
            context (str): retrieved context.
            answer (str): generated answer.

        Returns:
            float: A value between 0 and 1. 0 being no evidence found and 1 being supported by context.
        """

        reason, info = self._factuality_doc_in_out(
            context, answer
        )
        factuality_scores = {}
        i = 0
        for line in reason.split('\n'):
            if "Score" in line:
                factuality_scores[f"statement_{i}"] = re_0_10_rating(line) / 10
                i += 1

        return factuality_scores, {"reasons": reason}, info

    def coherence_with_cot_reasons_qa(self, prompt, response: str):
        system_prompt = str.format(CustomPrompts.COHERENCE_PROMPT_QA,
                                   query=prompt,
                                   response=response
                                   )
        system_prompt = system_prompt.replace(
            "RELEVANCE:", prompts.COT_REASONS_TEMPLATE
        )
        return self.generate_score_and_reasons(system_prompt)
        # return self._langchain_evaluate_with_cot_reasons(text, criteria)

    def fluency_with_cot_reasons(self, text: str):
        system_prompt = str.format(CustomPrompts.FLUENCY_V2,
                                   text=text,
                                   )
        return self.generate_score_and_reasons(system_prompt)

    def comprehensiveness_with_cot_reasons(self, source: str,
                                           summary: str):
        system_prompt = str.format(CustomPrompts.SUMMARIZATION_PROMPT_V2,
                                   source=source,
                                   summary=summary)
        return self.generate_score_and_reasons(system_prompt)

    def conciseness_with_cot_reasons(self, text: str):
        system_prompt = str.format(CustomPrompts.CONCISENESS_PROMPT_V2,
                                   text=text,
                                   )
        return self.generate_score_and_reasons(system_prompt)

    def coherence_with_rejection(self, text: str):
        system_prompt = str.format(CustomPrompts.COHERENCE_PROMPT_V2,
                                   text=text,
                                   )
        system_prompt = system_prompt.replace(
            "RELEVANCE:", prompts.COT_REASONS_TEMPLATE
        )
        return self.generate_score_and_reasons(system_prompt)

    def coherence_with_cot_reasons(self, text: str):
        system_prompt = str.format(CustomPrompts.COHERENCE_PROMPT_V3,
                                   text=text)
        return self.generate_score_and_reasons(system_prompt)

    def qs_relevance_with_few_shot(self, question: str, context: str):
        system_prompt = str.format(CustomPrompts.QS_Relevance_FS,
                                   question=question,
                                   context=context
                                   )
        # return self.generate_score_and_reasons(system_prompt)
        return self.endpoint.run_in_pace(
            func=self._create_chat_completion,
            prompt=system_prompt
        )

    def qs_relevance_with_cot_reasons_v2(self, question: str, context: str):
        system_prompt = str.format(CustomPrompts.QS_Relevance_V2,
                                   question=question,
                                   context=context
                                   )

        system_prompt = system_prompt.replace(
            "RELEVANCE:", prompts.COT_REASONS_TEMPLATE
        )
        print(system_prompt)
        return self.generate_score_and_reasons(system_prompt)

    def controversiality_with_cot_reasons_v2(self, text: str):
        system_prompt = str.format(CustomPrompts.CONTROVERSIALITY_PROMPT_V2,
                                   text=text
                                   )
        system_prompt = system_prompt.replace(
            "Controversiality:", prompts.COT_REASONS_TEMPLATE
        )
        return self.generate_score_and_reasons(system_prompt)

    def misogyny_with_cot_reasons_v2(self, text: str):
        system_prompt = str.format(CustomPrompts.MISOGYNY_PROMPT_V2,
                                   text=text
                                   )
        system_prompt = system_prompt.replace(
            "Misogyny:", prompts.COT_REASONS_TEMPLATE
        )
        return self.generate_score_and_reasons(system_prompt)

