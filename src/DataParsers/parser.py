from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyMuPDFLoader
import pathlib
from src import Constants
# from langchain_community.document_loaders.pdf import UnstructuredPDFLoader

base_chunking_config = {"size": 2400,
                        "overlap": 200}

golden_chunking_config = {"size": 1600,
                          "overlap": 200}


def web_loader(urls, vectordb, is_golden):
    if is_golden:
        chunking_config = golden_chunking_config
    else:
        chunking_config = base_chunking_config
    loader = WebBaseLoader(urls)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunking_config.get("size"),
                                                   chunk_overlap=chunking_config.get("overlap"))
    splits = text_splitter.split_documents(docs)
    vectordb.add_documents(documents=splits)
    return splits if is_golden else []


def pdf_loader(paths, vectordb, is_golden):
    chunks = []
    if is_golden:
        chunking_config = golden_chunking_config
    else:
        chunking_config = base_chunking_config
    for path in paths:
        # loader = UnstructuredPDFLoader(path)
        loader = PyMuPDFLoader(path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunking_config.get("size"),
                                                       chunk_overlap=chunking_config.get("overlap"))
        splits = text_splitter.split_documents(docs)
        if is_golden:
            chunks.append(splits)
        vectordb.add_documents(documents=splits)
    return chunks


def parser(paths, vectordb, is_golden=False):
    pdf_paths = []
    urls = []
    web_chunks = []
    pdf_chunk_list = []
    for path in paths:
        if pathlib.Path(path).suffix == ".pdf":
            pdf_paths.append(path)
        else:
            urls.append(path)
    print("count before: ", vectordb._collection.count())
    try:
        if urls:
            web_chunks = web_loader(urls, vectordb, is_golden)
    except Exception as e:
        print("web failed", str(e))
    print(pdf_paths)
    if pdf_paths:
        pdf_chunk_list = pdf_loader(pdf_paths, vectordb, is_golden)
    print("count after: ", vectordb._collection.count())
    pdf_chunk_list.append(web_chunks)
    return pdf_chunk_list
