from src.Utilities.SetupUtilities import SetUpUtilities
from src.DataParsers.parser import parser


class VectorDb:
    def __init__(self):
        self.app_vectors = "app_vectors"
        self.golden_vectors = "ground_vectors"
        self.setup_utilities = SetUpUtilities()
        self.db = self.setup_utilities.setup_vector_database_client(self.app_vectors)
        self.gdb = self.setup_utilities.setup_vector_database_client(self.golden_vectors)
        print("count: ", self.db._collection.count())

    def add_to_db(self, paths, is_golden=False):
        if is_golden:
            chunk_list = parser(paths, self.gdb, is_golden)
        else:
            chunk_list = parser(paths, self.db, is_golden)
        return chunk_list
