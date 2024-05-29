import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from simpletransformers.language_representation import RepresentationModel
from src.config_file import truncation, padding, max_length, return_tensors, num_beams, num_return_sequences, \
    temperature, skip_special_tokens, similarity_score
from sentence_transformers import SentenceTransformer, util


def calculate_context_relevance(base_sentence, sentences):
    model = SentenceTransformer("stsb-roberta-large")
    base_embedding = model.encode(base_sentence, convert_to_tensor=True)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(base_embedding, sentence_embeddings)[0]
    results = list(zip(sentences, similarities))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def rep_model(input_sentence, results):
    lang_model = RepresentationModel(
        model_type="bert",
        model_name="sentence-transformers/paraphrase-MiniLM-L6-v2",
        use_cuda=False)

    sentence_vec = lang_model.encode_sentences([input_sentence], combine_strategy='mean')
    predicted_sentence_vec = lang_model.encode_sentences(results, combine_strategy='mean')
    similarity_result = cosine_similarity(sentence_vec, predicted_sentence_vec)[0]
    results = list(zip(results, similarity_result))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


class PromptGeneration:
    model_name = 'tuner007/pegasus_paraphrase'
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

    def promptGenerate(self, input_sentence):
        try:
            results = []
            print(input_sentence)
            inputs = self.tokenizer([input_sentence], truncation=truncation,
                                    padding=padding,
                                    max_length=max_length,
                                    return_tensors=return_tensors).to(self.torch_device)
            translated = self.model.generate(**inputs, num_beams=num_beams,
                                             num_return_sequences=num_return_sequences, temperature=temperature)
            output_list = self.tokenizer.batch_decode(translated,
                                                      skip_special_tokens=skip_special_tokens)
            for i in range(len(output_list)):
                results.append(output_list[i])

            Representation_model_result = rep_model(input_sentence, results)
            for sentence, similarity in Representation_model_result:
                print(f"Similarity: {similarity:.4f}, Sentence: {sentence}")
            print("-------")
            context_relevance_results = calculate_context_relevance(input_sentence, results)
            for sentence, similarity in context_relevance_results:
                print(f"Similarity: {similarity:.4f}, Sentence: {sentence}")
            return context_relevance_results
        except Exception as e:
            import sys
            print(str(e), ' : ', str(sys.exc_info()[-1].tb_lineno))
            return {"resultStatus": "ERROR",
                    "resultMessage": "Error while generating Recommendations. Error is: " + str(e)}
