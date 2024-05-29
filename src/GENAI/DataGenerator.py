from langchain_core.documents import Document
from flask import Blueprint, jsonify, send_file
from flask import request
from werkzeug.exceptions import HTTPException
from src.GENAI.DataGenDbOperations import DataGenerator
from bson import ObjectId
from src.LlmLayer.AzureOpenAI import AzureOpenAILlm
from src.LlmLayer.LiteLLM import LiteLlm
from src.Utilities.utils import unique_id_generator
from src.Utilities.Rerank import ContextReranker
from src.Utilities.SimilarityFilter import SimilarityFilter
import pandas as pd
from datetime import datetime
from bson import ObjectId
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:\\gen_ai_asuurance_2078155\\qea-gen-ai-assurance\\vectordb_data'  # Define the upload folder path
ALLOWED_EXTENSIONS = {'pdf', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'wav', 'mp3','docx'}  # Define allowed file extensions


from src.daolayer import VectorReadWrite
import json
from src.daolayer import MongoReadWrite

router = Blueprint(
    'data-gen', __name__, )

ranker = ContextReranker()
similarity_filter = SimilarityFilter()
mongo_obj = MongoReadWrite.mongoReadWrite()
obj1=LiteLlm()

@router.route("/create_data", methods=["POST"])
def create_data(datasetId):
    try:
        output = build_ground_truth_data(datasetId)
        return output

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def build_ground_truth_data(datasetId):
    data_gen_obj = DataGenerator()
    dataset = list(data_gen_obj.load_by_id(datasetId, 'dataset'))[0]
    file_paths = dataset["file_paths"]
    model_type = dataset["model"]
    if not file_paths:
        raise ValueError("Missing 'file_paths' parameter in request data")

    # Process file paths
    vector_obj = VectorReadWrite.VectorDb()
    chunk_list = vector_obj.add_to_db(file_paths.split(","), is_golden=True)
    df = obj1.generate_question_chain(chunk_list, model_type)
    file_name = f"Query_dataset_GT_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(file_name, index=False)

    # store questions
    data_gen_obj = DataGenerator()
    data_gen_obj.add_golden_data(df, datasetId)
    questions = data_gen_obj.load_golden_questions(datasetId)
    retriever = vector_obj.gdb.as_retriever()
    run_id = unique_id_generator()
    answers = []
    # generate and store answers to generated questions
    for q_dict in questions:
        print(q_dict["question"])
        context = retriever.get_relevant_documents(q_dict["question"])

        context = [d.page_content for d in context]
        # print(context)
        final_answer = obj1.basic_qa_chain(q_dict["question"], context,model_type)
        answers.append({
            "datasetId": datasetId,
            "question_id": q_dict["_id"],
            "question": q_dict["question"],
            "answer": final_answer,
            "context": context,
            "run_id": run_id
        })

    data_gen_obj.store_answers(answers, is_golden=True)

    return jsonify({"datasetId": datasetId, "message": "Golden Data generated successfully"}), 200
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500


@router.route("/generate_bot_responses")
async def generate_bot_response():
    loaded_data = request.json
    data_gen_obj = DataGenerator()
    if (loaded_data.get("type")=='predefined_ques'):
        questions = data_gen_obj.load_golden_questions(loaded_data.get('datasetId'))
    elif(loaded_data.get("type")=='test_ques'):
        questions = data_gen_obj.load_test_questions(loaded_data.get('datasetId'))
    questions = list(questions)
    vector_obj = VectorReadWrite.VectorDb()
    retriever = vector_obj.db.as_retriever()
    run_id = unique_id_generator()
    answers = []
    # generate and store answers to generated questions
    datasetId = loaded_data.get('datasetId')
    dataset = list(data_gen_obj.load_by_id(datasetId, 'dataset'))[0]
    model_type = dataset["model"]
    for q_dict in questions:
        print(q_dict["question"])
        context = retriever.get_relevant_documents(q_dict["question"])
        context = [d.page_content for d in context]
        print(context)
        final_answer = obj1.basic_qa_chain(q_dict["question"], context,model_type)

        answers.append({
            "question_id": str(q_dict["_id"]),
            "question": q_dict["question"],
            "answer": final_answer,
            "context": context,
            "run_id": run_id,
            "datasetId": loaded_data.get('datasetId'),
            "source":"generated"
        })
    data_gen_obj.store_answers(answers)
    return jsonify({"message": "Bot Responses generated successfully",'source':'generated'}), 200


@router.route("/evaluate_responses_with_golden_data")
def evaluate_responses():
    loaded_data = request.json
    data_gen_obj = DataGenerator()
    golden_responses = data_gen_obj.load_responses(loaded_data.get('datasetId'),is_golden=True)  # predefined_questions_answers
    app_responses = data_gen_obj.load_responses(loaded_data.get('datasetId'))  # bot_question_answer
    datasetId = loaded_data.get('datasetId')
    dataset = list(data_gen_obj.load_by_id(datasetId, 'dataset'))[0]
    model_type = dataset["model"]
    # llm_object = LiteLlm()
    question_dict = {}
    for ares in app_responses:
        question_dict[ares["question_id"]] = {"app_answer": ares["answer"],
                                              "app_context": ares["context"]}

    for q in golden_responses:
        qid = str(ObjectId(q["question_id"]))
        if question_dict.get(qid):
            question_dict[qid]["gold_answer"] = q["answer"]

    for k in question_dict.keys():
        question_obj = list(data_gen_obj.load_single_question(k))
        if question_obj:
            question_dict[k]["question"] = question_obj[0].get("question")
    df = pd.DataFrame(
        columns=['question_id', 'question', 'ground_truth_answer', 'app_under_test_answer',
                 'app_under_test_retrieved_context', 'similarity_score', 'llm_similarity'])
    quota = 10

    for key, values in question_dict.items():
        app_response = values['app_answer']
        golden_response = values['gold_answer']
        similarity_score = similarity_filter.calculate_similarity(app_response, golden_response)
        question_dict[key]['similarity_score'] = similarity_score
        question_dict[key]['LLM_similarity'] = obj1.evaluate_chain(golden_response, app_response,model_type)
        # question_dict[key]['LLM_similarity'] = 0.7
        ddict = {"question_id": key, 'question': values["question"], 'ground_truth_answer': golden_response,
                 'app_under_test_answer': app_response, 'app_under_test_retrieved_context': values['app_context'],
                 'similarity_score': similarity_score,
                 'llm_similarity': question_dict[key]['LLM_similarity']}
        df_the_dict = pd.DataFrame.from_dict([ddict], orient="columns")
        df = pd.concat([df, df_the_dict], ignore_index=True)

    print(question_dict)
    file_name = f"Query_dataset_both_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(file_name, index=False)

    return jsonify({"message": "Bot Responses evaluated successfully"}), 200


@router.route("/get_context")
def get_context():
    # compressor = FlashrankRerank()
    # compression_retriever = ContextualCompressionRetriever(
    #     base_compressor=compressor, base_retriever=retriever
    # )
    #
    # compressed_docs = compression_retriever.get_relevant_documents(
    #     "What did the president say about Ketanji Jackson Brown"
    # )
    data_gen_obj = DataGenerator()
    df = pd.DataFrame(columns=['question_id', 'question', 'source_chunk', 'retrieved_context', 'reranked_context'])
    questions = data_gen_obj.load_golden_questions()
    vector_obj = VectorReadWrite.VectorDb()
    retriever = vector_obj.db.as_retriever(search_kwargs={"k": 6})
    # ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/opt")
    chunks = {}
    for q_dict in questions:
        print(q_dict["question"])
        if q_dict.get('chunk_id') not in chunks:
            chunk = data_gen_obj.load_by_id(q_dict.get('chunk_id'), data_gen_obj.data_chunks_collection)
            chunk = list(chunk)
            chunk = chunk[0]
            chunk['_id'] = str(chunk['_id'])
            chunks[chunk['_id']] = chunk['text']
        else:
            chunk = chunks[q_dict.get('chunk_id')]
        context = retriever.get_relevant_documents(q_dict["question"])
        # passages = [
        #     {"id": i, "text": doc.page_content} for i, doc in enumerate(context)
        # ]
        # rerankrequest = RerankRequest(query=q_dict["question"], passages=passages)
        # results = ranker.rerank(rerankrequest)
        results = ranker.rerank(q_dict["question"], context)
        context = [d.page_content for d in context]
        print(context)
        final_results = []
        for r in results:
            doc = Document(
                page_content=r["text"],
                metadata={"id": r["id"], "relevance_score": r["score"]},
            )
            final_results.append(doc)
        print(final_results)
        ddict = {
            'question_id': str(q_dict["_id"]),
            'question': q_dict["question"],
            'source_chunk': chunk['text'],
            'retrieved_context': "\n\n".join([str(c) for c in context]),
            'reranked_context': "\n\n".join([str(c) for c in final_results])
        }
        df_the_dict = pd.DataFrame.from_dict([ddict], orient="columns")
        df = pd.concat([df, df_the_dict], ignore_index=True)
    file_name = f"Context_reranked_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(file_name, index=False)

    return jsonify({"message": "Context retrieved and stored successfully"}), 200


@router.route("/load_data", methods=["POST"])
def load_data():
    try:
        # Check if the POST request has the file part
        if 'file' not in request.files:
            raise ValueError("No file part")

        files = request.files.getlist("file")

        # Initialize an empty list to store file paths
        file_paths_list = []

        # Iterate through each file
        for file in files:
            if file.filename == '':
                continue

            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(file.filename)

            # Save the file to the upload folder
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Add the file path to the list
            file_paths_list.append(file_path)

            # Process file paths
            # No need to split file_path here
            vector_obj = VectorReadWrite.VectorDb()
            vector_obj.add_to_db([file_path])  # Pass the file_path as a list

        print("list::", file_paths_list)

        # Extract datasetId from request data
        dataset_id = request.form.get("datasetId")
        if not dataset_id:
            raise ValueError("Missing 'datasetId' parameter in request data")

        # Update the file_paths parameter in the dataset collection based on datasetId
        dataset = mongo_obj.read_single_data('dataset', dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID '{dataset_id}' not found.")

        # Update the file_paths parameter
        dataset['file_paths'] = ','.join(file_paths_list)
        dataset['totalRecords'] = len(file_paths_list)

        # Write the updated dataset document back to the database
        mongo_obj.update_single_data('dataset', dataset, dataset_id)

        # Return success response
        return jsonify({"message": "Data loaded and file paths updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route("/create_dataset", methods=["POST"])
def create_dataset():
    try:
        loaded_data = request.json

        if mongo_obj.read_single_data_with_filter('dataset', loaded_data.get('datasetName'), 'datasetName'):
            raise ValueError(f"Dataset with name '{loaded_data.get('datasetName')}' already exists.")

        loaded_data['executedDate'] = loaded_data['modifiedDate'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        datasetId = mongo_obj.write_single_data('dataset', loaded_data)
        data = create_data(datasetId)
        return jsonify({"datasetId": datasetId, "message": "Dataset generated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
