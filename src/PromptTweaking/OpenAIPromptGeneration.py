from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config_file import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, num_return_sequences
from src.PromptTweaking.PromptGeneration import calculate_context_relevance, rep_model
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts.prompt import PromptTemplate


class OpenAIPromptGeneration:

    def promptGenerate(self, input_sentence):
        try:
            llm_model = AzureChatOpenAI(
                openai_api_version="2023-03-15-preview",
                deployment_name="gpt35exploration",
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY
            )
            prompt = ChatPromptTemplate.from_template("I am giving you a sample statement, you need to generate "
            "statements without changing their context {statement}." "{Instruction} Do not generate any answer for the given statement")
            chain = prompt | llm_model
            llm_response = chain.invoke(
                {"statement": f"generate {num_return_sequences} statements for {input_sentence}",
                 "Instruction": "Do not generate any answer for the given statement"})

            original_sentences = llm_response.content
            cleaned_sentences = [sentence.strip() for sentence in original_sentences.splitlines() if sentence.strip()]
            results = [sentence.split('. ', 1)[1] if '. ' in sentence else sentence for sentence in
                       cleaned_sentences]

            Representation_model_result = rep_model(input_sentence, results)
            for sentence, similarity in Representation_model_result:
                print(f"Similarity: {similarity:.4f}, Sentence: {sentence}")
            print("-------")
            context_relevance_results = calculate_context_relevance(input_sentence, results)
            for sentence, similarity in context_relevance_results:
                print(f"Similarity: {similarity:.4f}, Sentence: {sentence}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"resultStatus": "ERROR", "resultMessage": "Error: " + str(e)}
