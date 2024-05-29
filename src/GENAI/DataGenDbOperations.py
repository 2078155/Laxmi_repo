from src.daolayer import MongoReadWrite
import ast
from src import Constants
from bson import ObjectId


class DataGenerator:
    database = MongoReadWrite.mongoReadWrite()
    question_answer_collection = Constants.APP_QUESTION_ANSWER_COLLECTION
    predefined_question_collection = Constants.APP_PREDEFINED_QUESTION_COLLECTION
    predefined_question_answer_collection = Constants.APP_PREDEFINED_QUESTION_ANSWER_COLLECTION
    data_chunks_collection = Constants.APP_DATA_CHUNK_COLLECTION
    test_questions_collection =Constants.APP_TEST_QUESTIONS_COLLECTION

    def add_golden_data(self, df, datasetId):
        files = df['file'].tolist()
        chunks = df['Context'].tolist()
        queries = []
        for q in df['Questions'].tolist():
            print("questions--------------------",q)
            try:
                if not isinstance(q, list):
                    q = ast.literal_eval(q)
                queries.append(q)
            except Exception as e:
                print(e)
                continue
        print(queries)
        key_topics = []
        for q in df['Key Topics'].tolist():
            try:
                if not isinstance(q, list):
                    q = ast.literal_eval(q)
                print(q, type(q))
                key_topics.append(q)
            except:
                continue
        print(key_topics)

        for f, c, ql, kl in zip(files, chunks, queries, key_topics):
            try:
                # store chunk
                write_dict = {"datasetId": datasetId,
                              "file": f,
                              "text": c,
                              "key_topics": kl
                              }
                c_id = self.database.write_single_data(self.data_chunks_collection, write_dict)
                if c_id:
                    ql_dict = [{"chunk_id": c_id, "question": q, "datasetId": datasetId} for q in ql]
                    self.database.write_multiple_data(self.predefined_question_collection, ql_dict)
            except Exception as e:
                print(e)

    def load_golden_questions(self, datasetId):
        questions = self.database.read_data(self.predefined_question_collection, datasetId, "datasetId")
        return questions

    def load_test_questions(self, datasetId):
        questions = self.database.read_data(self.test_questions_collection, datasetId, "datasetId")
        return questions

    def store_answers(self, answer_list, is_golden=False):
        if is_golden:
            self.database.write_multiple_data(self.predefined_question_answer_collection, answer_list)
        else:
            self.database.write_multiple_data(self.question_answer_collection, answer_list)

    def load_responses(self, datasetId, is_golden=False):
        if is_golden:
            responses = list(self.database.read_data(self.predefined_question_answer_collection,datasetId, "datasetId"))
            print("g res")
            print(responses)
        else:
            responses = list(self.database.read_data(self.question_answer_collection,datasetId, "datasetId"))
        return responses

    def load_single_question(self, q_id):
        return self.database.read_data(self.predefined_question_collection, ObjectId(q_id), '_id')

    def load_by_id(self, d_id, collection):
        return self.database.read_data(collection, ObjectId(d_id), '_id')
