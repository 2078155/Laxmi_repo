import os

# from langchain_community.chat_models import AzureChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from src.Utilities.SetupUtilities import setup_utilities
from langchain.chains import LLMChain
from langchain.prompts import load_prompt
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import logging


logging.basicConfig(filename='llm.log', level=logging.INFO)
class AzureOpenAILlm:
    def __init__(self):

        self.llm_config = setup_utilities.setup_llm_model_config()

        self.azure_openai_llm = AzureChatOpenAI(deployment_name=self.llm_config.get("deployment_name"),
                                                model_name=self.llm_config.get("model_name"),
                                                temperature=self.llm_config.get("temperature"))

        self.token_length_factor = self.llm_config.get("token_length_factor")
        self.max_total_tokens = self.llm_config.get("max_total_tokens")
        # self.allowed_topics = startup_utilities.get_config_dict().get("allowed_topics")
        #
        # print(self.allowed_topics)
    #     self.thoughts = []
    #     self.actions = []
    #     self.observations = []
    #
    # def track_thought(self, thought):
    #     self.thoughts.append(thought)
    #     print(f"Thought: {thought}")
    #
    # def track_action(self, action):
    #     self.actions.append(action)
    #     print(f"Action: {action}")
    #
    # def track_observation(self, observation):
    #     self.observations.append(observation)
    #     print(f"Observation: {observation}")

    def basic_qa_chain(self, question, context):

        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks. Use the following pieces of retrieved information to answer the question.
                            If you can't answer the question based on the information, just say that you don't know. Use three sentences maximum and keep the answer concise.
                            \nQuestion: {question} \nInformation: {context} \nAnswer:
                            
                            """
                            ,
            input_variables=["question", "context"]
        )
        rag_chain = LLMChain(llm=self.azure_openai_llm, prompt=prompt)
        # self.track_observation(rag_chain.invoke({"question": question, "context": context}).get("text", "Nothing"))
        # self.track_action(rag_chain.invoke({"question": question, "context": context}).get("text", "Nothing"))
        # self.track_thought(rag_chain.invoke({"question": question, "context": context}).get("text", "Nothing"))

        return rag_chain.invoke({"question": question, "context": context}).get("text", "Nothing")

        # output = rag_chain.invoke({"question": question, "context": context})
        # thought = output.get("thought", "Nothing")
        # action = output.get("action", "Nothing")
        # observation = output.get("observation", "Nothing")
        # primary_output = output.get("text", "Nothing")
        # return primary_output, thought, action, observation



    def evaluate_chain(self, golden, app):

        prompt = PromptTemplate(
            template="""
            Paragraph 1: {golden}
            \n\n
            Paragraph 2: {app}
            \n\n
            Score paragraph 2 on it's similarity to Paragraph one from 0.0 to 1.0, where 1.0 means near identical, answer should only be a floating point number with 1 number after decimal.
            Answer:
            """,
            input_variables=["golden", "ans"]
        )
        rag_chain = LLMChain(llm=self.azure_openai_llm, prompt=prompt)
        # self.track_observation(rag_chain.invoke({"golden": golden, "app": app}).get("text", "Nothing"))
        # self.track_thought(rag_chain.invoke({"golden": golden, "app": app}).get("text", "Nothing"))
        # self.track_action(rag_chain.invoke({"golden": golden, "app": app}).get("text", "Nothing"))

        return rag_chain.invoke({"golden": golden, "app": app}).get("text", "Nothing")
        # output = rag_chain.invoke({"golden": golden, "app": app})
        # thought = output.get("thought", "Nothing")
        # action = output.get("action", "Nothing")
        # observation = output.get("observation", "Nothing")
        # primary_output = output.get("text", "Nothing")
        # return primary_output, thought, action, observation



    def generate_question_chain(self, chunk_list):
        # self.track_action("generate_question_chain")
        parser = JsonOutputParser()

        prompt = PromptTemplate(
            template="""Your task is to write 2 questions based on the context. The questions should be diverse in nature
                covering the information in the context document. Don't make the questions too direct, rather they should be questions that can be answered if a person has knowleddge present in the given text. Do not write answers for the questions.
                \n Context: {context}.
                \n Provide the output as a JSON, with 2 fields
                'Questions' which is a list of questions, and 'Key Topics' which is a list of upto 3 main key topics of the passage
                 do not add numbering to the questions or key topics, the JSON will be converted to a python dictionary.
                 """,
            input_variables=["context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.azure_openai_llm | parser
        df = pd.DataFrame(columns=['file', 'Context', 'Questions', 'Key Topics'])
        for source_chunks in chunk_list:
            for chunk in source_chunks:
                try:
                    if len(chunk.page_content) > 500:

                        output = chain.invoke({"context": chunk.page_content})
                        print(output)
                        # self.track_observation(output)
                        # self.track_action(output)
                        # self.track_thought(output)
                        ddict = {"file": chunk.metadata.get('source'), 'Context': chunk.page_content,
                                 'Questions': output.get("Questions"), 'Key Topics': output.get('Key Topics')}
                        print(ddict)
                        df_the_dict = pd.DataFrame.from_dict([ddict], orient="columns")
                        # output = chain.invoke({"context": chunk.page_content})
                        # thought = output.get("thought", "Nothing")
                        # action = output.get("action", "Nothing")
                        # observation = output.get("observation", "Nothing")
                        # ddict = {"file": chunk.metadata.get('source'), 'Context': chunk.page_content,
                        #          'Questions': output.get("Questions"), 'Key Topics': output.get('Key Topics'),
                        #          'Thought': thought, 'Action': action, 'Observation': observation}
                        # df_the_dict = pd.DataFrame.from_dict([ddict], orient="columns")
                        df = pd.concat([df, df_the_dict], ignore_index=True)
                except Exception as e:
                    print(e)
        return df