from bson import ObjectId
from pymongo import MongoClient


class mongoReadWrite:
    def _connect_mongo(self):
        conn = MongoClient(
            "mongodb://genaiUser:genaiuserPwd@localhost:27017/?authSource=GenAiAssuranceDatabase")
        return conn["GenAiAssuranceDatabase"]
        # conn = MongoClient(
        #     "mongodb://localhost:27017/"
        # )
        # return conn["ragbotdbflask"]

    def write_multiple_data(self, collection_name, data_list):
        db = self._connect_mongo()
        db_with_collection = db[collection_name]
        db_with_collection.insert_many(data_list)

    def write_single_data(self, collection_name, data):
        db = self._connect_mongo()
        db_with_collection = db[collection_name]
        result = db_with_collection.insert_one(data)
        document_id = result.inserted_id
        document_id_str = str(document_id)
        return document_id_str

    def update_single_data(self, collection_name, data, document_id):
        db = self._connect_mongo()
        query = {'_id': ObjectId(document_id), "$set": data}
        if self.sanitize_update_query(query):
            query_id = {'_id': ObjectId(document_id)}
            query_data = {"$set": data}
            cursor = db[collection_name].update_one(query_id, query_data)
            return cursor
        else:
            return None

    def update_data(self, collection_name, update_data,filter_query):
        db = self._connect_mongo()
        if self.sanitize_update_query(update_data):
            cursor = db[collection_name].update_one(filter_query, update_data)
            return cursor
        else:
            return None

    def read_data(self, collection_name, filterColumnValue=None, filterColumn=None):
        db = self._connect_mongo()

        if filterColumnValue is None or filterColumn is None:
            # If no filter criteria provided, retrieve all documents
            cursor = db[collection_name].find()
        else:
            # Construct query with provided filter criteria
            query = {filterColumn: filterColumnValue}
            if self.sanitize_query(query):
                cursor = db[collection_name].find(query)
            else:
                return None

        return cursor

    def read_single_data_with_filter(self, collection_name, filterColumnValue, filterColumn):
        db = self._connect_mongo()
        cursor = db[collection_name].find_one({filterColumn: filterColumnValue})
        return cursor

    def read_single_data(self, collection_name, document_id):
        # self.logger.info("inside read_single_data")
        db = self._connect_mongo()
        cursor = db[collection_name].find_one({'_id': ObjectId(document_id)})
        return cursor

    def sanitize_query(self, query):
        flag = True
        for key in query.keys():
            if key.startswith('$'):
                flag = False
        return flag

    def sanitize_update_query(self, query):
        flag = True
        for key in query.keys():
            if not key.startswith(("_", "$")):
                flag = False
        return flag
