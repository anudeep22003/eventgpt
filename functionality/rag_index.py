from urllib.parse import SplitResult, urlunsplit
import os

from llama_index import (
    Document,
    VectorStoreIndex,
    get_response_synthesizer,
    SummaryIndex,
)
from llama_index.text_splitter import get_default_text_splitter
from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt

from llama_index.node_parser import SimpleNodeParser
from llama_index.retrievers import VectorIndexRetriever

from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor

from app import models, schemas, crud, db
from app.deps import get_db
from functionality.extract import check_if_domain_exists, IndexEventPage
import constants
from prompts import text_qa_template

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(f"logs/{__name__}.log", mode="a")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

PATH_RAG_INDEX = "./data/Rag-Index"


class QueryRagIndex:
    def __init__(self, urlsplit_obj: SplitResult):
        self.urlsplit_obj = urlsplit_obj
        self.rag_index = self.retreive_index()

    def is_domain_downloaded(self):
        "check if domain is in db"
        with get_db() as db:
            domain_from_db = crud.domain.get_domain_by_name(
                db=db, domain=self.urlsplit_obj
            )
        if domain_from_db is None:
            return False
        return True

    def retreive_index(self):
        #! does not work to create a new index. Only uses past index.
        index_dir = os.path.join(os.getcwd(), PATH_RAG_INDEX, self.urlsplit_obj.netloc)
        "check if index dir exists and is empty, if so build index, else retreive index"
        dir_exists_on_filesystem = os.path.exists(index_dir)
        # try catch block to see if dir is empty even if directory does not exist
        try:
            dir_is_full = bool(os.listdir(index_dir))
        except FileNotFoundError:
            dir_is_full = False

        if dir_exists_on_filesystem and dir_is_full:
            #! even when indexing fails an empty index file gets created so this check is not sufficient
            logger.debug("index dir exists and is not empty")
            sc = StorageContext.from_defaults(persist_dir=index_dir)
            rag_index = load_index_from_storage(sc, index_id=self.urlsplit_obj.netloc)
            logger.debug(f"Existing index loaded from {index_dir}")
            return rag_index

        elif (not dir_exists_on_filesystem) or not dir_is_full:
            logger.debug(
                "index dir exists but is empty"
                if dir_exists_on_filesystem
                else "index dir does not exist"
            )
            b = BuildRagIndex(urlsplit_obj=self.urlsplit_obj)
            rag_index = b.rag_index
            logger.debug(f"Built index at {index_dir}")
            return rag_index
        else:
            # capturing for completeness, but this path should not be reached
            logger.debug("Soemthing weird happened - #12334")
            raise Exception("Something weird happened - #12334")

    def query_index(self, query_text: str):
        "query the index for a given query"
        max_nodes = constants.MAX_NUM_NODES_TO_SYNTHESIZE_RESPONSE
        num_lines_in_node_threshold = constants.MIN_NUM_LINES_THRESHOLD

        retriever = VectorIndexRetriever(
            index=self.rag_index, similarity_top_k=constants.SIMILARITY_TOP_K_LVL_1
        )

        # ------- level 1 retieval
        retrieved_nodes = retriever.retrieve(query_text)
        # ------- level 2 retrieval (remove nodes with little text)
        line_threshold_nodes = [
            node_with_score
            for node_with_score in retrieved_nodes
            if node_with_score.text
        ]
        level2_retrieved_nodes = [
            node_with_score
            for node_with_score in retrieved_nodes
            if node_with_score.score > 0.75
        ]
        if len(level2_retrieved_nodes) < max_nodes:
            retrieved_nodes = retrieved_nodes[:1]
        # -------- level 3 retreival
        # if number of nodes more than max_nodes defined in constants file just use the top
        #! if number of nodes less than max, then use at least 1
        #! if score of retrieved nodes is less than 0.75, then use at least 1

        if len(retrieved_nodes) > max_nodes:
            retrieved_nodes = retrieved_nodes[:max_nodes]

        # # configure response synthesizer
        response_synthesizer = get_response_synthesizer(
            response_mode="compact_accumulate"
        )

        # construct index to query using retreived nodes
        query_index = SummaryIndex(
            nodes=[node_with_score.node for node_with_score in retrieved_nodes],
        )

        # assemble query engine
        query_engine = query_index.as_query_engine(
            response_synthesizer=response_synthesizer,
            text_qa_template=text_qa_template,
            # streaming=True
        )

        response = query_engine.query(
            query_text,
        )
        return response


class BuildRagIndex:
    def __init__(self, urlsplit_obj: SplitResult):
        self.urlsplit_obj = urlsplit_obj
        self.site_url_objs = self.get_domain_siteurl_db_objs()
        self.rag_index = self.build_rag_index()

    def save_rag_index(self, rag_index: VectorStoreIndex):
        "save the rag index to the disk"
        "store in directory, if directory does not exist create it"
        dir_to_save_index = os.path.join(
            os.getcwd(), PATH_RAG_INDEX, self.urlsplit_obj.netloc
        )
        if not os.path.exists(dir_to_save_index):
            os.makedirs(dir_to_save_index)
        rag_index.set_index_id(self.urlsplit_obj.netloc)
        rag_index.storage_context.persist(persist_dir=dir_to_save_index)

    def get_prompt(self) -> Prompt:
        return Prompt(
            """You are an agent trained to assist humans in a conversational form. Use the context of the human's and your own responses above to best answer the below query as an agent. Use only the context information without relying on prior knowledge. Respond in markdown format. Be detailed in your answer but also don't repeat yourself. \nIf you are unable to answer using the given context, respond with "The organizer does not seem to have shared this information. Try visiting the website yourself." \n\nAnswer the following question: {query_str}\n"""
        )

    def get_domain_siteurl_db_objs(self) -> list[models.siteurl.SiteUrl]:
        "get all the urls for the domain stored in the db"
        with get_db() as db:
            site_urls = crud.siteurl.get_urls_by_domain(
                db=db, domain=self.urlsplit_obj.netloc
            )
        return site_urls

    def get_url_text(self, url: str):
        "for a given url, get the text stored in the db"
        return [s.text for s in self.site_url_objs if s.url == url]

    def percent_of_siteurl_objs_with_no_text(
        self, site_url_objs: list[models.siteurl.SiteUrl]
    ) -> float:
        "get the percentage of siteurl objects with no text"
        return len([s for s in site_url_objs if not s.text]) / len(site_url_objs)

    def restrict_siteurl_objs_to_ones_without_text(
        self, site_url_objs: list[models.siteurl.SiteUrl]
    ) -> list[models.siteurl.SiteUrl]:
        "restrict the siteurl objects to ones without text"
        return [
            s
            for s in site_url_objs
            if not s.text
            # this is good enough, because for failed webpage the string "None" is stored
            # So even if the text is "None" it will be counted as text
            # and you dont need to check for None
        ]

    def build_rag_index(self):
        "if siteurls are none, then you will have to first index the event page"
        logger.debug(f"---> building rag index for {urlunsplit(self.urlsplit_obj)}")
        if not (self.site_url_objs):
            logger.debug(
                "no siteurls found, so building the index from downloading the event page"
            )
            IndexEventPage(urlsplit_obj=self.urlsplit_obj)
            self.site_url_objs = self.get_domain_siteurl_db_objs()
        else:
            non_text_nodes = self.restrict_siteurl_objs_to_ones_without_text(
                self.site_url_objs
            )
            if not (non_text_nodes):
                logger.debug(
                    "siteurls found, all have text, so building the index from the db"
                )
            else:
                logger.debug(
                    f"total siteurls {len(self.site_url_objs)} and {len(non_text_nodes)/len(self.site_url_objs)} percent have no text"
                )
                IndexEventPage(urlsplit_obj=self.urlsplit_obj)
                self.site_url_objs = self.get_domain_siteurl_db_objs()
        "construct doc, nodes and finally index for querying"
        parser = SimpleNodeParser(text_splitter=get_default_text_splitter())

        documents = [Document(doc_id=s.url, text=s.text) for s in self.site_url_objs]
        nodes = parser.get_nodes_from_documents(documents, show_progress=True)
        rag_index = VectorStoreIndex(nodes)
        self.save_rag_index(rag_index)
        return rag_index

    def query_rag_index(self, query_text: str):
        "query the index for a given query"
        retriever = VectorIndexRetriever(
            index=self.rag_index,
            # similarity_top_k=1
        )

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
