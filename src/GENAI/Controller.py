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
import json
from src.daolayer import MongoReadWrite

mongo_obj = MongoReadWrite.mongoReadWrite()

router = Blueprint(
    'controller', __name__, )


@router.route("/edit_dataset/<dataset_id>", methods=["PUT"])
def edit_dataset(dataset_id):
    try:
        updated_data = request.json

        # Convert dataset_id to ObjectId
        dataset_id = ObjectId(dataset_id)

        # Retrieve the dataset by its ID
        dataset = mongo_obj.read_single_data('dataset', dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID '{dataset_id}' not found.")

        # Update the dataset document with the new data
        for key, value in updated_data.items():
            dataset[key] = value

        # Update the modified date
        dataset['modifiedDate'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Write the updated dataset document back to the database
        mongo_obj.update_single_data('dataset', dataset,dataset_id )

        return jsonify({"message": "Dataset updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route('/get_dataset_details', methods=['GET'])
def get_documents():
    try:
        # Receive project name from the request body as JSON data
        data = request.json
        project_name = data.get('project_name')

        # Query MongoDB to retrieve documents based on project name
        documents = list(mongo_obj.read_data('dataset',project_name , 'projectName'))

        print(documents)
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        return  documents, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@router.route('/upload_excel', methods=['POST'])
def upload_excel():
    print("inside upload excel")

    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    dataset_id = request.form.get('datasetId')  # Get datasetId from the request form

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file is an Excel file
    if file and file.filename.endswith('.xlsx'):
        print("File received and it is an Excel file.")
        try:
            # Generate a unique runId
            run_id = unique_id_generator()

            # Read Excel file into DataFrame
            df = pd.read_excel(file)

            # Check if the DataFrame contains necessary columns
            if 'question' in df.columns and 'answer' in df.columns:

                # Define a function to split the context into chunks of 500 words each
                def split_context_into_chunks(context, chunk_size):
                    words = context.split()
                    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

                # Define the chunk size (in words)
                chunk_size = 500

                if 'context' in df.columns:
                    # Split context into chunks of 500 words and store each chunk as a separate string in a list
                    df['context'] = df['context'].apply(lambda x: split_context_into_chunks(str(x), chunk_size))
                else:
                    # Assign empty list to context column if absent
                    df['context'] = df.apply(lambda _: [], axis=1)

                # Add datasetId, source, and runId to DataFrame
                df['datasetId'] = dataset_id
                df['source'] = 'uploaded'
                df['runId'] = run_id

                # Store questions, answers, context, source, and runId in ques_ans collection
                data = df[['datasetId', 'question', 'answer', 'context', 'source', 'runId']].to_dict(orient='records')
                mongo_obj.write_multiple_data('bot_question_answer',data)

                responses = list(mongo_obj.read_data('bot_question_answer', dataset_id, 'datasetId'))
                print(responses)
                # Convert ObjectId fields to strings
                for response in responses:
                    response['_id'] = str(response['_id'])
                return jsonify({'message': 'uploaded successfully', 'responses': responses}), 200
            else:
                return jsonify({'error': 'Invalid Excel file format. Missing required columns'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file format. Please upload a .xlsx file'}), 400

@router.route('/download_excel_template', methods=['GET'])
def download_excel_template():
    # Path to your Excel template file
    excel_template_path = 'C:\prompt_template.xlsx'
    try:
        # Send the file to the client for download
        return send_file(excel_template_path, as_attachment=True)
    except Exception as e:
        return str(e), 500

@router.route('/fetch_ques_responses', methods=['GET'])
def fetch_ques_responses():
    try:
        # Receive project name from the request body as JSON data
        data = request.json
        datasetId = data.get('datasetId')

        # Query MongoDB to retrieve documents based on project name
        documents = list(mongo_obj.read_data('bot_question_answer', datasetId, 'datasetId'))

        print(documents)
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        return jsonify({'message': 'fetched successfully', 'responses': documents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@router.route('/fetch_ques', methods=['GET'])
def fetch_ques():
    try:
        # Receive project name from the request body as JSON data
        data = request.json
        datasetId = data.get('datasetId')

        # Query MongoDB to retrieve documents based on project name
        documents = list(mongo_obj.read_data('predefined_questions', datasetId, 'datasetId'))

        print(documents)
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        return jsonify({'message': 'fetched successfully', 'responses': documents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@router.route("/update_answer", methods=["PUT"])
def update_answer():
    try:
        # Receive dataset ID, question, new answer, and verification flag from the request body as JSON
        data = request.json
        dataset_id = data.get('dataset_id')
        question = data.get('question')
        new_answer = data.get('new_answer')
        is_verified = data.get('is_verified', False)  # Default value False if not provided

        # Update the answer in the bot_ques_answer collection
        filter_query = {'datasetId': dataset_id, 'question': question}
        update_query = {'$set': {'answer': new_answer, 'is_verified': is_verified}}
        mongo_obj.update_data('bot_question_answer', update_query, filter_query)

        return jsonify({"message": "Answer updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

