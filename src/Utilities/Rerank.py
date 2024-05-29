from flashrank import Ranker, RerankRequest


class ContextReranker:
    def __init__(self):
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/opt")

    def rerank(self, query, context):
        """

        :param query: str user given prompt
        :param context: langchain retriever output list[Document]
        :return: list re-ranked passages
        """
        passages = [
            {"id": i, "text": doc.page_content} for i, doc in enumerate(context)
        ]
        rerankrequest = RerankRequest(query=query, passages=passages)
        return self.ranker.rerank(rerankrequest)
