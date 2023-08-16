from urllib.parse import urlparse
import os

from llama_index import Document, VectorStoreIndex, get_response_synthesizer
from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt

from llama_index.node_parser import SimpleNodeParser
from llama_index.retrievers import VectorIndexRetriever

from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor

from app import models, schemas, crud, db
from app.deps import get_db

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(f"logs/{__name__}.log", mode="a")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

PATH_RAG_INDEX = "./data/Rag-Index"


class QueryRagIndex:
    def __init__(self, domain: str):
        self.domain = domain
        self.rag_index = self.retreive_index()

    def is_domain_downloaded(self):
        "check if domain is in db"
        with get_db() as db:
            domain_from_db = crud.domain.get_domain_by_name(db=db, domain=self.domain)
        if domain_from_db is None:
            return False
        return True

    def retreive_index(self):
        #! does not work to create a new index. Only uses past index.
        if self.is_domain_downloaded():
            logger.debug("domain is downloaded")
            sc = StorageContext.from_defaults(persist_dir=PATH_RAG_INDEX)
            try:
                rag_index = load_index_from_storage(sc, index_id=self.domain)
                logger.debug("Existing index loaded")
                return rag_index
            except Exception as e:
                logger.debug("No Rag Index found, exception encountered: ", e)
                logger.debug(
                    "---------------- building index from downloaded html files"
                )
                b = BuildRagIndex(domain=self.domain)
                rag_index = b.rag_index
                logger.debug(f"Built index at {PATH_RAG_INDEX}")
                return rag_index
        else:
            logger.debug("downloading files, and then building index.")
            b = BuildRagIndex(domain=self.domain)
            rag_index = b.rag_index
            logger.debug(f"Downloaded html files and then built index")
            return rag_index

    def query_index(self, query_text: str):
        "query the index for a given query"
        retriever = VectorIndexRetriever(index=self.rag_index, similarity_top_k=3)

        # configure response synthesizer
        response_synthesizer = get_response_synthesizer()

        # assemble query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            # text_qa_template=self.get_prompt(),
        )
        response = query_engine.query(query_text)
        return response


class BuildRagIndex:
    def __init__(self, domain: str):
        self.domain = domain
        self.site_url_objs = self.get_domain_siteurl_db_objs()
        self.rag_index = self.build_rag_index()

    def save_rag_index(self, rag_index: VectorStoreIndex):
        "save the rag index to the disk"
        rag_index.set_index_id(self.domain)
        rag_index.storage_context.persist(persist_dir=PATH_RAG_INDEX)

    def get_prompt(self) -> Prompt:
        return Prompt(
            """You are an agent trained to assist humans in a conversational form. Use the context of the human's and your own responses above to best answer the below query as an agent. Use only the context information without relying on prior knowledge. Respond in markdown format. Be detailed in your answer but also don't repeat yourself. \nIf you are unable to answer using the given context, respond with "The organizer does not seem to have shared this information. Try visiting the website yourself." \n\nAnswer the following question: {query_str}\n"""
        )

    def get_domain_siteurl_db_objs(self) -> list[models.siteurl.SiteUrl]:
        "get all the urls for the domain stored in the db"
        with get_db() as db:
            site_urls = crud.siteurl.get_urls_by_domain(db=db, domain=self.domain)
        return site_urls

    def get_url_text(self, url: str):
        "for a given url, get the text stored in the db"
        return [s.text for s in self.site_url_objs if s.url == url]

    def build_rag_index(self):
        "construct doc, nodes and finally index for querying"
        parser = SimpleNodeParser()

        documents = [Document(doc_id=s.url, text=s.text) for s in self.site_url_objs]
        nodes = parser.get_nodes_from_documents(documents)
        rag_index = VectorStoreIndex(nodes)
        self.save_rag_index(rag_index)
        return rag_index

    def query_rag_index(self, query_text: str):
        "query the index for a given query"
        retriever = VectorIndexRetriever(index=self.rag_index, similarity_top_k=3)

        # configure response synthesizer
        response_synthesizer = get_response_synthesizer()

        # assemble query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            # text_qa_template=self.get_prompt(),
        )
        response = query_engine.query(query_text)
        return response
