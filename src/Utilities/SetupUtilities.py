import json
import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma


from langchain_community.embeddings import SentenceTransformerEmbeddings


class SetUpUtilities(object):

    def __init__(self):
        load_dotenv()
        self.akm_home = os.getenv('App_home')
        print(self.akm_home)
        self.llm_model_name = os.getenv('llm_model')
        config_path = os.path.join(self.akm_home, "Config", "config.json")
        with open(config_path) as handle:
            self.config_dict = json.loads(handle.read())
        print(self.config_dict)

    def setup_vector_database_client(self, collection_name):

        chroma_db_path = os.path.join(self.akm_home, self.config_dict.get("chroma_db_config").get("chroma_db_path"))
        embedding_model = self.config_dict.get("chroma_db_config").get("embedding_model")
        embedding_function = SentenceTransformerEmbeddings(model_name=embedding_model)
        vectordb = Chroma(persist_directory=chroma_db_path, embedding_function=embedding_function, collection_name=collection_name)
        return vectordb

    def setup_llm_model_config(self):
        model_config_dict = {}
        if self.llm_model_name == "gpt3":
            model_config_dict['deployment_name'] = self.config_dict.get("llm_config").get("gpt3").get("deployment_name")
            model_config_dict['model_name'] = self.config_dict.get("llm_config").get("gpt3").get("model_name")
            model_config_dict['temperature'] = float(self.config_dict.get("llm_config").get("gpt3").get("temperature"))
            model_config_dict['token_length_factor'] = float(self.config_dict.get("llm_config").get("gpt3").get("token_length_factor"))
            model_config_dict['max_total_tokens'] = int(self.config_dict.get("llm_config").get("gpt3").get("max_total_tokens"))
        return model_config_dict

    # def get_database(self, db_type: str = None, db_config_dict=None):
    #     """
    #     Initializes Database
    #     :param db_type: name of db to be loaded from config
    #     :param db_config_dict: configuration details for the db
    #     :return: object of mongo_data_interface class
    #     """
    #     if db_type == 'mongo_db':
    #         return MongoDbConnector(db_config_dict)
    #     else:
    #         raise ValueError("Unsupported NoSQL Database type")


setup_utilities = SetUpUtilities()
