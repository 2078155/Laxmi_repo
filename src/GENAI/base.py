import spacy
from afinn import Afinn


class Addedmetrics:

    # def llm_concisenses(self, query: str):
    #     nlp = spacy.load('en_core_web_sm')
    #     doc = nlp(query)
    #     # Calculate the number of tokens in the sentence
    #     num_tokens = len(doc)
    #     # Return the evaluation based on sentence length
    #     if num_tokens <= 10:
    #         return "Concise"
    #     elif num_tokens <= 20:
    #         return "Reasonably Concise"
    #     else:
    #         return "Not Concise"

    def llm_contoversiality(self, query: str):
        afinn = Afinn(language='en')
        controversiality_threshold = -2
        examples = [query]
        for example in examples:
            sentiment_score = afinn.score(example)
            if sentiment_score < controversiality_threshold:
                answer = "The text is controversial."
            else:
                answer = "The text is not controversial."
            print("Example:", example)
            print("Answer:", answer)
            print("Sentiment Score:", sentiment_score)
            return sentiment_score

    # def llm_factuality(self, query: str, answer: str):
    #     nlp = spacy.load("en_core_web_sm")
    #     # Define a list of known facts
    #     reference = [query]
    #     # Calculate similarity scores using Spacy's similarity function
    #     similarity_scores = [nlp(answer).similarity(nlp(fact)) for fact in reference]
    #     # Find the maximum similarity score
    #     max_score = max(similarity_scores)
    #     # Set a threshold for factuality
    #     threshold = 0.7
    #     # Determine factuality based on the maximum similarity score
    #     if max_score >= threshold:
    #         factuality = "Correct"
    #     else:
    #         factuality = "Incorrect"
    #     return factuality, max_score
