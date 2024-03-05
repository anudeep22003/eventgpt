# define a custom retriever

from llama_index.schema import NodeWithScore
from llama_index import QueryBundle, VectorStoreIndex
from llama_index.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
)

import constants as C

import typing as T


class CustomRetriever(BaseRetriever):
    """Defining a custom retriever

    Args:
        BaseRetriever (_type_): _description_
    """

    def __init__(self, index: VectorStoreIndex) -> None:
        """Initialize params"""
        self._vec_retriever = self._initialize_vector_retriever(index)

    def _initialize_vector_retriever(
        self, index: VectorStoreIndex
    ) -> VectorIndexRetriever:
        return VectorIndexRetriever(
            index=index,
            similarity_top_k=C.SIMILARITY_TOP_K_LVL_1,
            # vector_store_query_mode=...,
            filter=None,  # metadata filter go in here
        )

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        pass

    def _retrieve_topk_nodes(self, query_bundle: QueryBundle) -> l[NodeWithScore]:
        vector_nodes = self._vec_retriever.retrieve(query_bundle)
        vector_nodes = {n.node.node_id for n in vector_nodes}
        return vector_nodes

    def _filter_low_info_nodes(
        self, node_list: list[NodeWithScore]
    ) -> list[NodeWithScore]:
        num_sentences_cutoff = C.MIN_NUM_LINES_THRESHOLD
        node_content = [(idx, n.node.get_content()) for idx, n in enumerate(node_list)]
        ids_that_clear_threshold = [idx for idx, n_content in node_content if ...]

        return [n for n in node_list if n.node.get_content()]
        pass

    ######## Utility functions ########

    def number_of_sentence(self, text: str) -> int:
        import re

        line_sep = re.compile(r"[\n\r]+")
