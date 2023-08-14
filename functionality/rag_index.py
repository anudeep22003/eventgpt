from urllib.parse import urlparse

from llama_index import Document, VectorStoreIndex, get_response_synthesizer
from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt

from llama_index.node_parser import SimpleNodeParser
from llama_index.retrievers import VectorIndexRetriever

from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor

from app import models, schemas, crud, db
from app.deps import get_db


class QueryRagIndex:
    def __init__(self, domain: str):
        self.domain = urlparse(url=domain).netloc
        ...

    def is_domain_indexed(self):
        "check if domain is already indexed"
        with get_db() as db:
            domain_from_db = crud.domain.get_domain_by_name(db=db, domain=self.domain)
        if domain_from_db is None:
            return False
        return True

    def retreive_index(self):
        ...

    def respond_to_query(self, query_text: str) -> str:
        "respond to query"
        ...


class BuildRagIndex:
    def __init__(self, domain: str):
        self.domain = urlparse(domain).netloc
        self.site_urls = self.get_domain_urls()
        self.rag_index = self.build_rag_index()
        self.save_rag_index()
        ...

    def get_prompt(self) -> Prompt:
        return Prompt(
            """You are an agent trained to assist humans in a conversational form. Use the context of the human's and your own responses above to best answer the below query as an agent. Use only the context information without relying on prior knowledge. Respond in markdown format. Be detailed in your answer but also don't repeat yourself. \nIf you are unable to answer using the given context, respond with "The organizer does not seem to have shared this information. Try visiting the website yourself." \n\nAnswer the following question: {query_str}\n"""
        )

    def get_rag_index(self):
        return self

    def get_domain_urls(self) -> list[models.siteurl.SiteUrl]:
        "get all the urls for the domain stored in the db"
        with get_db() as db:
            site_urls = crud.siteurl.get_urls_by_domain(db=db, domain=self.domain)
        return site_urls

    def get_url_text(self, url: str):
        "for a given url, get the text stored in the db"
        return [s.text for s in self.site_urls if s.url == url]

    def build_rag_index(self):
        "construct doc, nodes and finally index for querying"
        parser = SimpleNodeParser()

        documents = [Document(doc_id=s.url, text=s.text) for s in self.site_urls]
        nodes = parser.get_nodes_from_documents(documents)
        return VectorStoreIndex(nodes)

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

    def save_rag_index(self):
        "save the rag index to the disk"
        self.rag_index.storage_context.persist(persist_dir="./data/rag_index")
