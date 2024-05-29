import json
import boto3
from litellm import completion
import litellm
import os
from src.config_file import  OPENAI_API_KEY,AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION,MODEL_ENGINE, \
    Deployment_Name,SERVICE_NAME,REGION_NAME,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
import logging
import pandas as pd
import time
from langchain_core.output_parsers import JsonOutputParser
from src.LlmLayer.Count import count_characters_and_words

log_info=litellm.set_verbose=True

## set AZURE_OPEN_AI ENV variables
os.environ["AZURE_API_KEY"] = OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = OPENAI_API_VERSION
os.environ["MODEL_ENGINE"]= MODEL_ENGINE
# Claude ENV variables
os.environ["SERVICE_NAME"] = SERVICE_NAME
os.environ["REGION_NAME"] = REGION_NAME
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY

class LiteLlm:
    def __init__(self):
        self.char_count=0
        self.word_count=0

    def basic_qa_chain(self, question, context, model_type):
        print(model_type,"from basic_qa_chain")
        prompt_template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved information to answer the question. If you can't answer the question based on the information, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question} 
        Information: {context} 
        Answer:"""
        text = '\n\n'.join(context)
        final_text = f"{question} {text}"
        char_count_input, word_count_input = count_characters_and_words(final_text)
        formatted_prompt = prompt_template.format(question=question, context=context)

        if (model_type=="gpt-35-turbo"):
            response = litellm.completion(
                model=f"azure/{Deployment_Name}",
                messages=[{"content": formatted_prompt, "role": "user"}],
                api_key=OPENAI_API_KEY
            )

        elif (model_type=="claude-v3"):

            bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name="us-east-1",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )
            response = completion(
                model='bedrock/anthropic.claude-3-sonnet-20240229-v1:0',
                messages=[{"role": "user","content": formatted_prompt }],
                aws_bedrock_client=bedrock,
            )

        # response = litellm.completion(
        #     model=f"azure/{Deployment_Name}",
        #     messages=[{"content": formatted_prompt, "role": "user"}],
        #     api_key=OPENAI_API_KEY
        # )

        if 'choices' in response and len(response['choices']) > 0:
            answer = response['choices'][0].get('message', {}).get('content', '')
            char_count_output, word_count_output = count_characters_and_words(answer)
            self.char_count += char_count_input + char_count_output
            self.word_count += word_count_input + word_count_output
            return answer
        else:
            return None


    def evaluate_chain(self, golden, app,model_type):
        prompt_template = """Paragraph 1: {golden}
    
            Paragraph 2: {app}
    
            Score paragraph 2 on its similarity to Paragraph one from 0.0 to 1.0, where 1.0 means near identical, answer should only be a floating point number with 1 number after decimal.
            Answer:"""

        formatted_prompt = prompt_template.format(golden=golden, app=app)
        final_text = f"{golden} {app}"
        char_count_input, word_count_input = count_characters_and_words(final_text)
        if (model_type == "gpt-35-turbo"):
            response = litellm.completion(
                f"azure/{Deployment_Name}",
                messages=[{"content": formatted_prompt ,"role": "user"}],
                api_key=OPENAI_API_KEY
            )

        elif (model_type=="claude-v3"):

            bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name="us-east-1",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )
            response = completion(
                model='bedrock/anthropic.claude-3-sonnet-20240229-v1:0',
                messages=[{"role": "user","content": formatted_prompt }],
                aws_bedrock_client=bedrock,
            )
        logging.info(f"evaluate_chain: Golden - {golden}, App - {app}, Response - {response}")

        if 'choices' in response and len(response['choices']) > 0:
            score = float(response['choices'][0].get('message', {}).get('content', ''))
            char_count_output, word_count_output = count_characters_and_words(score)
            self.char_count += char_count_input + char_count_output
            self.word_count += word_count_input + word_count_output
            return score
        else:
            return None

    def generate_question_chain(self, chunk_list, model_type):
        parser = JsonOutputParser()
        df = pd.DataFrame(columns=['file', 'Context', 'Questions', 'Key Topics'])
        for source_chunks in chunk_list:
            for chunk in source_chunks:
                try:
                    if len(chunk.page_content) > 0:
                        prompt_template = f"""Your task is to write 2 questions based on the context. The questions should be diverse in nature
                                    covering the information in the context document. Don't make the questions too direct, rather they should be questions that can be answered if a person has knowledge present in the given text. Do not write answers for the questions.
                                    \n Context: {chunk.page_content}.
                                    \n Provide the output as a JSON, with 2 fields
                                    'Questions' which is a list of questions, and 'Key Topics' which is a list of up to 3 main key topics of the passage
                                    do not add numbering to the questions or key topics, the JSON will be converted to a python dictionary.
                                 """
                        char_count_input, word_count_input = count_characters_and_words(chunk.page_content)
                        if (model_type == "gpt-35-turbo"):
                            output =  litellm.completion(
                                f"azure/{Deployment_Name}",
                                api_key=OPENAI_API_KEY,
                                messages=[{"content": prompt_template, "role": "user"}],
                            )
                        elif (model_type == "claude-v3"):
                            bedrock = boto3.client(
                                service_name="bedrock-runtime",
                                region_name="us-east-1",
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            )
                            output = completion(
                                model='bedrock/anthropic.claude-3-sonnet-20240229-v1:0',
                                messages=[{"role": "user","content": prompt_template }],
                                aws_bedrock_client=bedrock,
                            )
                        content_dict = json.loads(output['choices'][0]['message']['content'])
                        output_str = json.dumps(content_dict, separators=(',', ':'))
                        start_index = output_str.find("{")
                        cleaned_string = output_str[start_index:]
                        char_count_output, word_count_output = count_characters_and_words(cleaned_string)

                        ddict = {
                            "file": chunk.metadata.get('source'),
                            'Context': chunk.page_content,
                            'Questions': content_dict.get('Questions', []),
                            'Key Topics': content_dict.get('Key Topics',[])
                        }

                        df_the_dict = pd.DataFrame.from_dict([ddict], orient="columns")
                        df = pd.concat([df, df_the_dict], ignore_index=True)
                        self.char_count += char_count_input + char_count_output
                        self.word_count += word_count_input + word_count_output
                except Exception as e:
                    print(e)
        return df

# if __name__ == "__main__":
#     lite_llm = LiteLlm()
#     question = "What is the capital of France?"
#     context = "France is known for its cheese, wine, and history. It has many cities, including Paris, Lyon, and Marseille."
#     print("Question:", question)
#     print("Context:", context)
#     result = lite_llm.basic_qa_chain(question, context)
#     print("Generated Answer:", result)
#
#     golden = "Paris is the capital of France."
#     app = "The capital of France is Paris."
#     score = lite_llm.evaluate_chain(golden, app)
#     print("Similarity Score:", score)
#
#     chunk_list = [
#         [
#             {
#                 "page_content": "France is known for its cheese, wine, and history.",
#                 "metadata": {"source": "SampleSource1"}
#             },
#             {
#                 "page_content": "Paris is the capital of France.",
#                 "metadata": {"source": "SampleSource2"}
#             }
#         ],
#         [
#             {
#                 "page_content": "The Eiffel Tower is located in Paris.",
#                 "metadata": {"source": "SampleSource3"}
#             },
#             {
#                 "page_content": "French cuisine includes dishes like coq au vin and escargot.",
#                 "metadata": {"source": "SampleSource4"}
#             }
#         ]
#     ]
#
#     df_result = lite_llm.generate_question_chain(chunk_list)
#
#     print("Generated DataFrame:")
#     print(df_result)
#     print("DataFrame Shape:", df_result.shape)
#     print("Columns:", df_result.columns)
#
