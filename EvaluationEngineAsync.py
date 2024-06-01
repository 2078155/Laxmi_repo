import asyncio
import os
import time
from trulens_eval.feedback.provider.hugs import Huggingface
# from trulens_eval.feedback.provider import AzureOpenAI
from langkit.openai import OpenAIAzure
import numpy as np
from src.GENAI.base import Addedmetrics
from src.config_file import OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION, HUGGINGFACE_API_KEY, \
    Deployment_Name,SERVICE_NAME,REGION_NAME,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
from src.GENAI.PiiDetection import PiiDetector
# from trulens_eval import LiteLLM
from trulens_eval.feedback.provider.litellm import LiteLLM
from src.GENAI.base import Addedmetrics
from litellm import completion_cost
# log_info = litellm.set_verbose = True
os.environ["AZURE_API_KEY"] = OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = OPENAI_API_VERSION
os.environ["HUGGINGFACE_API_KEY"] = HUGGINGFACE_API_KEY
# Claude ENV variables
os.environ["SERVICE_NAME"] = SERVICE_NAME
os.environ["AWS_REGION_NAME"] = REGION_NAME
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
# openai = AzureOpenAI(deployment_name=Deployment_Name)
# gpt = OpenAIAzure(engine=Deployment_Name)
# api_key=OPENAI_API_KEY,
litellm = LiteLLM(model_engine="azure/gpt35exploration")
# litellmClaude = LiteLLM(model_engine="bedrock/anthropic.claude-instant-v1")
# litellmClaude = LiteLLM(model_engine="bedrock/anthropic.claude-3-haiku-20240307-v1:0")
litellmClaude = LiteLLM(model_engine="bedrock/anthropic.claude-3-sonnet-20240229-v1:0")
hug_provider = Huggingface()
pii_detector = PiiDetector()
baseobj = Addedmetrics()
class Feedback:

    def __init__(self, query=None, answer=None, context=None,model=None):
        self.query = query
        self.answer = answer
        self.context = context
        self.model = model
        self.latency = 0
        self.totalcost = 0

    async def async_method_wrapper(self, sync_method, *args, **kwargs):
        await asyncio.sleep(1)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: sync_method(*args, **kwargs))

    async def qs_relevance(self):
        return await self.async_method_wrapper(self.sync_qs_relevance)

    def sync_qs_relevance(self):
        start_time=0
        end_time=0
        # context_rel = openai.qs_relevance_with_cot_reasons(self.query, self.context)
        if(self.model == "gpt-35-turbo"):
            start_time=time.time()
            response,reason,info = litellm.qs_relevance_with_cot_reasons(self.query, self.context)
            end_time =time.time()
        elif(self.model == "claude-v3"):
            start_time = time.time()
            response,reason,info = litellmClaude.qs_relevance_with_cot_reasons(self.query, self.context)
            print("relevance\n\n\n")
            print("reason======\n\n\n",reason)
            print("\n\n\n\n")
            end_time = time.time()
        # reason = context_rel[1]['reason'].split(':')[2].strip()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return response, final_reason

    async def qa_relevance(self):
        return await self.async_method_wrapper(self.sync_qa_relevance)

    def sync_qa_relevance(self):
        start_time = 0
        end_time = 0
        # answer_rel = openai.relevance_with_cot_reasons(self.query, self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time = time.time()
            answer_rel,reason,info = litellm.relevance_with_cot_reasons(self.query, self.answer)
            end_time =time.time()
        elif (self.model == "claude-v3"):
            start_time = time.time()
            answer_rel,reason,info = litellmClaude.relevance_with_cot_reasons(self.query, self.answer)
            print("qarelevance\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time =time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return answer_rel, final_reason

    async def groundedness(self):
        return await self.async_method_wrapper(self.sync_groundedness)

    def sync_groundedness(self):
        start_time = 0
        end_time = 0
        from trulens_eval.feedback import Groundedness
        # grounded = Groundedness(groundedness_provider=openai)
        if (self.model == "gpt-35-turbo"):
            start_time = time.time()
            grounded = Groundedness(groundedness_provider=litellm)
            end_time =time.time()
        elif (self.model == "claude-v3"):
            start_time = time.time()
            grounded = Groundedness(groundedness_provider=litellmClaude)
            end_time = time.time()
        self.latency+=(end_time-start_time)
        grounded_tuple,reason,info = grounded.groundedness_measure_with_cot_reasons(self.answer, self.context)
        print("grounded\n\n\n")
        print("reason======\n\n\n", reason)
        print("\n\n\n\n")
        cost = completion_cost(completion_response=info)
        self.totalcost+=cost
        # statement_score = list(grounded_tuple[0].values())
        statement_score = list(grounded_tuple.values())
        print("groundedness\n\n\n",grounded_tuple)
        supporting_statement=reason['reasons'].split(':')[2].strip()
        # supporting_statement = ':'.join(reason['reasons'].split(':')[2:]).strip()
        return round(np.mean(statement_score), 1),supporting_statement

    async def coherence(self):
        return await self.async_method_wrapper(self.sync_coherence)

    def sync_coherence(self):
        start_time = 0
        end_time = 0
        # coherence_with_cot_reason = openai.coherence_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            coherence_with_cot_reason,reason,info = litellm.coherence_with_cot_reasons(self.answer)
            end_time = time.time()
        elif (self.model == "claude-v3"):
            start_time = time.time()
            coherence_with_cot_reason,reason,info = litellmClaude.coherence_with_cot_reasons(self.answer)
            print("coherence\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time = time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        # final_reason = reason['reason'].split('Supporting Evidence:')[1].strip()
        return coherence_with_cot_reason, final_reason

    async def summarization(self):
        return await self.async_method_wrapper(self.sync_summarization)

    def sync_summarization(self):
        start_time = 0
        end_time = 0
        # summarization = openai.comprehensiveness_with_cot_reasons(self.query, self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            summarization,reason,info = litellm.comprehensiveness_with_cot_reasons(self.query, self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            summarization,reason,info = litellmClaude.comprehensiveness_with_cot_reasons(self.query, self.answer)
            print("summarization\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return summarization, final_reason

    async def concisenses(self):
        return await self.async_method_wrapper(self.sync_concisenses)

    def sync_concisenses(self):
        start_time = 0
        end_time = 0
        # concisense = openai.conciseness_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            concisense,reason,info = litellm.conciseness_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            concisense,reason,info = litellmClaude.conciseness_with_cot_reasons(self.answer)
            print("conscisence\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return concisense, final_reason

    async def controversiality(self):
        return await self.async_method_wrapper(self.sync_controversiality)

    def sync_controversiality(self):
        start_time = 0
        end_time = 0
        # controversial = openai.controversiality_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            controversial,reason,info = litellm.controversiality_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            controversial,reason,info = litellmClaude.controversiality_with_cot_reasons(self.answer)
            print("controversial\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return controversial, final_reason

    async def correctness(self):
        return await self.async_method_wrapper(self.sync_correctness)

    def sync_correctness(self):
        start_time = 0
        end_time = 0
        # correct_sc = openai.correctness_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            correct_sc,reason,info = litellm.correctness_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            correct_sc,reason,info = litellmClaude.correctness_with_cot_reasons(self.answer)
            print("correct_sc\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return correct_sc, final_reason

    async def criminality(self):
        return await self.async_method_wrapper(self.sync_criminality)

    def sync_criminality(self):
        start_time = 0
        end_time = 0
        # criminal_sc = openai.criminality_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            criminal_sc,reason,info = litellm.criminality_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            criminal_sc,reason,info = litellmClaude.criminality_with_cot_reasons(self.answer)
            print("criminalsc\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return criminal_sc, final_reason

    async def harmfulness(self):
        return await self.async_method_wrapper(self.sync_harmfulness)

    def sync_harmfulness(self):
        start_time = 0
        end_time = 0
        # harmful = openai.harmfulness_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            harmful,reason,info = litellm.harmfulness_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            harmful,reason,info = litellmClaude.harmfulness_with_cot_reasons(self.answer)
            print("harmful\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return harmful, final_reason

    async def helpfulness(self):
        return await self.async_method_wrapper(self.sync_helpfulness)

    def sync_helpfulness(self):
        start_time = 0
        end_time = 0
        # helpful = openai.helpfulness_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            helpful,reason,info = litellm.helpfulness_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            helpful,reason,info = litellmClaude.helpfulness_with_cot_reasons(self.answer)
            print("harmfulness\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency+=(end_time-start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return helpful, final_reason

    async def insensitivity(self):
        return await self.async_method_wrapper(self.sync_insensitivity)

    def sync_insensitivity(self):
        start_time = 0
        end_time = 0
        # insensitive = openai.insensitivity_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            insensitive,reason,info = litellm.insensitivity_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            insensitive,reason,info = litellmClaude.insensitivity_with_cot_reasons(self.answer)
            print("insensitive\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return insensitive, final_reason

    async def maliciousness(self):
        return await self.async_method_wrapper(self.sync_maliciousness)

    def sync_maliciousness(self):
        start_time = 0
        end_time = 0
        # malicious = openai.maliciousness_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            malicious,reason,info = litellm.maliciousness_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            malicious,reason,info = litellmClaude.maliciousness_with_cot_reasons(self.answer)
            print("malicious\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return malicious, final_reason

    async def misogyny(self):
        return await self.async_method_wrapper(self.sync_misogyny)

    def sync_misogyny(self):
        start_time = 0
        end_time = 0
        # misogyny_sc = openai.misogyny_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            misogyny_sc,reason,info = litellm.misogyny_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            misogyny_sc,reason,info = litellmClaude.misogyny_with_cot_reasons(self.answer)
            print("misogyny\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return misogyny_sc, final_reason

    async def sentiment(self):
        return await self.async_method_wrapper(self.sync_sentiment)

    def sync_sentiment(self):
        start_time = 0
        end_time = 0
        # sentiment_sc = openai.sentiment_with_cot_reasons(self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            sentiment_sc,reason,info = litellm.sentiment_with_cot_reasons(self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            sentiment_sc,reason,info = litellmClaude.sentiment_with_cot_reasons(self.answer)
            print("sentimentsc\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return sentiment_sc, final_reason

    async def stereotype(self):
        return await self.async_method_wrapper(self.sync_stereotype)

    def sync_stereotype(self):
        start_time = 0
        end_time = 0
        # stereotype_sc = openai.stereotypes_with_cot_reasons(self.query, self.answer)
        if (self.model == "gpt-35-turbo"):
            start_time=time.time()
            stereotype_sc,reason,info = litellm.stereotypes_with_cot_reasons(self.query, self.answer)
            end_time=time.time()
        elif (self.model == "claude-v3"):
            start_time=time.time()
            stereotype_sc,reason,info= litellmClaude.stereotypes_with_cot_reasons(self.query, self.answer)
            print("stereotypesc\n\n\n")
            print("reason======\n\n\n", reason)
            print("\n\n\n\n")
            end_time=time.time()
        self.latency += (end_time - start_time)
        cost = completion_cost(completion_response=info)
        self.totalcost += cost
        final_reason = reason['reason'].split(':')[2].strip()
        return stereotype_sc, final_reason

    # async def pii_detection(self):
    #     return await self.async_method_wrapper(self.sync_pii_detection)
    #
    # def sync_pii_detection(self):
    #     pii = hug_provider.pii_detection_with_cot_reasons(self.answer)
    #     reason = list(pii[1].keys())
    #     time.sleep(1.5)
    #     return round(1 - pii[0], 1), ";".join(reason)

    async def pii_detection(self):
        return await self.async_method_wrapper(self.sync_pii_detection)

    def sync_pii_detection(self):
        # Use the pii_detector instance to analyze the answer text for PII
        start_time=time.time()
        pii_results = pii_detector.detect_pii(text=self.answer)
        end_time=time.time()
        self.latency+=(end_time-start_time)

        # Check if any PII is detected
        if pii_results:
            score = round(1 - pii_results[0].score, 1)
            reason_str = "Detected PII"
        else:
            score = 0.0
            reason_str = "No PII detected"

        time.sleep(1.5)
        # Return the score and reason string
        return score, reason_str

    async def toxicity(self):
        return await self.async_method_wrapper(self.sync_toxicity)

    def sync_toxicity(self):
        start_time=time.time()
        toxic = hug_provider.toxic(self.answer)
        end_time=time.time()
        self.latency+=(end_time-start_time)
        time.sleep(1.5)
        return round(toxic, 1)

    async def language_match(self):
        return await self.async_method_wrapper(self.sync_language_match)

    def sync_language_match(self):
        start_time=time.time()
        lan_match = hug_provider.language_match(self.query, self.answer)
        end_time=time.time()
        self.latency += (end_time - start_time)
        time.sleep(1.5)
        return round(lan_match[0], 1)

    async def llm_controversiality(self):
        return await self.async_method_wrapper(self.sync_llm_controversiality)

    def sync_llm_controversiality(self):
        return baseobj.llm_contoversiality(self.query)