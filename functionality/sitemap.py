from urllib.parse import SplitResult, urlunsplit
import os, requests
from typing import Any
from urllib.parse import urljoin, urlsplit, urlparse, urlunparse
from bs4 import BeautifulSoup
from collections import Counter
from app import crud, db, schemas, models
from app.deps import get_db
import logging
from usp.tree import sitemap_tree_for_homepage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(f"logs/{__name__}.log", mode="a")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


_UNPUBLISHED_SITEMAP_PATHS = {
    "sitemap.xml",
    "sitemap.xml.gz",
    "sitemap_index.xml",
    "sitemap-index.xml",
    "sitemap_index.xml.gz",
    "sitemap-index.xml.gz",
    ".sitemap.xml",
    "sitemap",
    "admin/config/search/xmlsitemap",
    "sitemap/sitemap-index.xml",
}
"""Paths which are not exposed in robots.txt but might still contain a sitemap."""


class SitemapBuilder:

    """Master class to build a sitemap for a given domain.
    This should be able to handle building sitemap for both:
    - domains that have a sitemap page
    - domains that do not have a sitemap page
    """

    def __init__(self) -> None:
        pass

    def __call__(
        self,
        urlsplit_obj: SplitResult,
        recursive_depth_cutoff: int = 3,
        pagerank_limit: int = 100,
    ) -> tuple[list, dict]:
        "takes a domain, and returns a sitemap and a pagerank"
        # get domain
        # check if sitemap exists
        parent_urlsplit_obj = SplitResult(
            scheme=urlsplit_obj.scheme,
            netloc=urlsplit_obj.netloc,
            path="/",
            query="",
            fragment="",
        )
        with get_db() as db:
            domain_from_db = crud.domain.get_domain_by_name(
                db=db, domain=parent_urlsplit_obj.netloc
            )
        if domain_from_db is None:
            logger.debug("Building from scratch")
            # if sitemap does not exist, recursively build a traverse dict
            sitemap = self.download_sitemap_if_exists(parent_urlsplit_obj)
            if sitemap is not None:
                logger.debug(f"Sitemap for {urlsplit_obj.netloc} exists")
                if len(sitemap) < pagerank_limit:
                    logger.debug(
                        f"Number of links is {len(sitemap)} building from sitemap"
                    )
                    pagerank = self.build_pagerank_from_sitemap(sitemap)
                else:
                    logger.debug(
                        f"Num of sitemap links: {len(sitemap)}. Limit is {pagerank_limit/len(sitemap):.2%} of all sitemap links. Building a sitemap from scratch."
                    )
                    #! repeat of the lines immediately after. Correct later.
                    urlpath_traverse_dict = self.build_ahref_traverse_dict(
                        parent_urlsplit_obj=parent_urlsplit_obj,
                        recursive_depth_cutoff=recursive_depth_cutoff,
                        pagerank_limit=pagerank_limit,
                    )
                    sitemap = self.get_sitemap(urlpath_traverse_dict)
                    pagerank = self.get_pagerank(urlpath_traverse_dict)
            else:
                urlpath_traverse_dict = self.build_ahref_traverse_dict(
                    parent_urlsplit_obj=parent_urlsplit_obj,
                    recursive_depth_cutoff=recursive_depth_cutoff,
                    pagerank_limit=pagerank_limit,
                )
                sitemap = self.get_sitemap(urlpath_traverse_dict)
                pagerank = self.get_pagerank(urlpath_traverse_dict)
            logger.debug(f"sitemap: {sitemap}")
            logger.debug(f"pagerank: {pagerank}")
        else:
            sitemap = domain_from_db.sitemap.split(" , ")
            pagerank = domain_from_db.pagerank
            logger.debug("Pulling from database")
            logger.debug(f"sitemap: {sitemap}")
            logger.debug(f"pagerank: {pagerank}")

        return sitemap, pagerank

    def download_sitemap_if_exists(self, urlsplit_obj: SplitResult) -> list:
        "get all possible sitemaps from the url"
        # dont need the below anymore because you are passing SplitResult object
        # constructed_url = self.construct_url(urlsplit_obj)
        sitemap_collection = sitemap_tree_for_homepage(urlunsplit(urlsplit_obj))
        all_urls = list(set([page.url for page in sitemap_collection.all_pages()]))
        if not bool(all_urls):
            return None
        return all_urls

    def manually_check_if_sitemap_exists(self, domain: str) -> bool:
        """check if sitemap exists for a given domain
        - use robots.txt or variations of sitemap locations to check
        - return location of sitemap if it exists, or False if it does not
        """
        # use robots.txt or variations of sitemap locations to check
        possible_sitemap_locations = {
            "sitemap.xml",
            "sitemap.xml.gz",
            "sitemap_index.xml",
            "sitemap-index.xml",
            "sitemap_index.xml.gz",
            "sitemap-index.xml.gz",
            ".sitemap.xml",
            "sitemap",
            "admin/config/search/xmlsitemap",
            "sitemap/sitemap-index.xml",
        }
        """Paths which are not exposed in robots.txt but might still contain a sitemap."""

        # first check if robots.txt exists
        res = requests.get(
            self.construct_url(domain, "robots.txt"), allow_redirects=True
        )
        if res.status_code == 200:
            robots_txt = res.text
            # check if sitemap is in robots.txt
            for line in robots_txt.split("\n"):
                if "Sitemap:" in line:
                    possible_sitemap_locations.add(line.split(" ")[1])
            # check if sitemap exists in any of the possible locations
            for path in possible_sitemap_locations:
                res = requests.get(self.construct_url(domain, path))
                if res.status_code == 200:
                    return True

        pass

    def download_existing_sitemap(self, sitemap_location: str) -> None:
        "download existing sitemap for a given domain"
        # use robots.txt or variations of sitemap locations to download
        pass

    def add_to_traverse_dict(
        self,
        url_or_path_from_ahrefs: str,
        parent_urlsplit_obj: SplitResult,
        traverse_dict: dict,
    ) -> None:
        "add url to traverse dict"
        # if url is not already in traverse dict, add it
        # you have to handle if url is of type '/careers/' as well as 'www.google.com/careers/'
        urlsplit_obj = urlsplit(url_or_path_from_ahrefs)
        if not urlsplit_obj.netloc:
            urlsplit_obj = SplitResult(
                scheme=parent_urlsplit_obj.scheme,
                netloc=parent_urlsplit_obj.netloc,
                path=urlsplit_obj.path,
                query=urlsplit_obj.query,
                fragment=urlsplit_obj.fragment,
            )

        urlpath = urlunsplit(urlsplit_obj)
        if urlpath not in traverse_dict:
            traverse_dict[urlpath] = {"visited": False, "pagerank": 1}
        else:
            traverse_dict[urlpath]["pagerank"] += 1
        return traverse_dict

    def build_ahref_traverse_dict(
        self,
        parent_urlsplit_obj: SplitResult,
        recursive_depth_cutoff: int,
        pagerank_limit: int,
    ) -> dict:
        "generate sitemap for a given domain"
        # use crawler to generate sitemap
        # save the full link of the path, not just the path
        current_recursion_depth = 0
        urlpath_traverse_dict = {
            urlunsplit(parent_urlsplit_obj): {"visited": False, "pagerank": 1}
        }

        def all_links_have_been_traversed() -> bool:
            return all([v["visited"] for v in urlpath_traverse_dict.values()])

        def num_links_traversed() -> int:
            return len([k for k, v in urlpath_traverse_dict.items() if v["visited"]])

        # keep entering the while loop for as long as
        # (1) all links have not been traversed,
        # (2) recursion depth has been exceeded, or
        # (3) num of links traversed is less than pagerank limit
        while (
            (not all_links_have_been_traversed())
            and (current_recursion_depth < recursive_depth_cutoff)
            and (num_links_traversed() < pagerank_limit)
        ):
            logger.debug(
                f"current_recursion_depth: {current_recursion_depth}"
            )  # logging
            logger.debug(f"num_links_traversed: {num_links_traversed()}")  # logging

            urlpaths_left_to_traverse = [
                urlpath
                for urlpath in urlpath_traverse_dict.keys()
                if urlpath_traverse_dict[urlpath]["visited"] == False
            ]

            logger.debug(
                f"paths left to traverse: {urlpaths_left_to_traverse}"
            )  # logging

            for urlpath in urlpaths_left_to_traverse:
                split_urlpath = urlsplit(urlpath)
                # you can get bot `/careers/` and `www.google.com/careers/` type urls
                # have to handle both
                path_list = self.get_internal_ahref_urlpaths(split_urlpath)
                logger.debug(f"link_list: {path_list}")  # logging
                for path in path_list:
                    if self.check_if_path_or_url_is_internal_and_parsable(
                        path=path, parent_urlsplit_obj=parent_urlsplit_obj
                    ):
                        urlpath_traverse_dict = self.add_to_traverse_dict(
                            url_or_path_from_ahrefs=path,
                            parent_urlsplit_obj=parent_urlsplit_obj,
                            traverse_dict=urlpath_traverse_dict,
                        )
                urlpath_traverse_dict[urlunsplit(split_urlpath)]["visited"] = True
                logger.debug(f"traverse_dict: {urlpath_traverse_dict}")  # logging
                logger.debug(
                    f"paths left to traverse: {urlpaths_left_to_traverse}"
                )  # logging
            current_recursion_depth += 1
        # clean up the traverse dict so as to remove the links you are not going to parse because a limit was exceeded
        cleaned_urlpath_traverse_dict = {
            k: v for k, v in urlpath_traverse_dict.items() if v["visited"]
        }

        total_urls_in_traverse_path = len(urlpath_traverse_dict.items())
        num_urls_within_limit = len(cleaned_urlpath_traverse_dict.items())
        logger.debug(
            f"Total number of urls on traverse path was {total_urls_in_traverse_path} and number discarded for exceeding limits was {total_urls_in_traverse_path - num_urls_within_limit}"
        )

        return cleaned_urlpath_traverse_dict

    def get_sitemap(self, traverse_dict: dict) -> list:
        "generate sitemap from traverse dict"
        return traverse_dict.keys()

    def get_pagerank(self, traverse_dict: dict) -> dict:
        "generate pagerank from traverse dict"
        return Counter(
            {urlpath: value["pagerank"] for urlpath, value in traverse_dict.items()}
        )

    def build_pagerank_from_sitemap(
        self, sitemap: list, pagerank_limit: int = 100
    ) -> dict:
        "generate pagerank from sitemap"
        pagerank = Counter()
        logger.debug(f"Sitemap length: {len(sitemap)}")
        for url in sitemap:
            urlsplit_obj = urlsplit(url)
            urlpath_list = self.get_internal_ahref_urlpaths(
                urlsplit_obj=urlsplit_obj,
            )
            urlpaths_to_add_to_pagerank = [
                urlpath
                for urlpath in urlpath_list
                if self.check_if_path_or_url_is_internal_and_parsable(
                    path=urlpath, parent_urlsplit_obj=urlsplit_obj
                )
            ]
            pagerank.update(urlpaths_to_add_to_pagerank)
            highest_pagerank = max(pagerank.values())
            if highest_pagerank > pagerank_limit:
                logger.debug(
                    f"num of links skipped due to pagerank limit: {len(sitemap) - len(pagerank)}"
                )
                break

        return pagerank

    def download_html_save_to_db(self, urlsplit_obj: SplitResult) -> None:
        constructed_url = urlunsplit(urlsplit_obj)
        with get_db() as db:
            siteurl = crud.siteurl.get_by_url(db=db, url=constructed_url)
            if siteurl is None:
                #! doing insecure thing, setting verify=false to allow websites that fail ssl certification verification
                html = requests.get(constructed_url, verify=False).text
                obj_in = schemas.SiteUrlCreate(
                    domain=urlsplit_obj.netloc, url=constructed_url, html=html
                )
                crud.siteurl.create(db=db, obj_in=obj_in)
            else:
                html = crud.siteurl.get_by_url(db=db, url=constructed_url).html
        return html

    def get_internal_ahref_urlpaths(self, urlsplit_obj: SplitResult) -> list:
        "get all internal links from a given domain and path"
        html = self.download_html_save_to_db(urlsplit_obj=urlsplit_obj)
        soup = BeautifulSoup(html, "html.parser")
        list_of_links = [
            link.get("href") for link in soup.find_all("a") if link.get("href")
        ]
        return list_of_links

    def check_if_path_or_url_is_internal_and_parsable(
        self,
        path: str,
        parent_urlsplit_obj: SplitResult,
    ) -> bool:
        "check if a url is internal to a given domain"
        skip_suffixes = {
            ".pdf",
            ".jpg",
            ".png",
            ".jpeg",
            ".gif",
            ".svg",
            ".PDF",
            ".JPG",
            ".PNG",
            ".JPEG",
            ".GIF",
            ".SVG",
        }
        split = urlsplit(path)
        # is it full url or only path
        if split.path.endswith(tuple(skip_suffixes)):
            return False
        if (
            not (split.netloc)
            and not (split.scheme)
            and split.path
            and split.path != "/"
        ):
            return True
        if split.netloc == parent_urlsplit_obj.netloc:
            return True
        return False


if __name__ == "__main__":
    i = SitemapBuilder()
    print(
        i.strip_url_to_homepage(
            "https://www.google.com/search?q=mac+right+key+is+auto+pressed&oq=mac+right+key+is+auto+pressed&aqs=chrome..69i57.5952j0j1&sourceid=chrome&ie=UTF-8"
        )
    )
