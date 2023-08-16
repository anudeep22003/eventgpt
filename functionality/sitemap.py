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

    def debug_call_(self, url: str) -> Any:
        domain = urlsplit(url).netloc
        logger.debug(f"url: {url}, parsed domain: {domain}")
        path_traverse_dict = self.build_ahref_traverse_dict(domain)
        sitemap = self.get_sitemap(path_traverse_dict)
        pagerank = self.get_pagerank(path_traverse_dict)
        return sitemap, pagerank

    def __call__(self, url: str) -> Any:
        "takes a domain, and returns a sitemap and a pagerank"
        # get domain
        domain = urlsplit(url).netloc
        # check if sitemap exists
        with get_db() as db:
            domain_from_db = crud.domain.get_domain_by_name(db=db, domain=domain)
        if domain_from_db is None:
            # if sitemap does not exist, recursively build a traverse dict
            sitemap = self.download_sitemap_if_exists(url)
            if sitemap is None:
                path_traverse_dict = self.build_ahref_traverse_dict(domain)
                sitemap = self.get_sitemap(path_traverse_dict)
                pagerank = self.get_pagerank(path_traverse_dict)
            else:
                pagerank = self.build_pagerank_from_sitemap(sitemap)
            logger.debug("Building from scratch")
            logger.debug(f"sitemap: {sitemap}")
            logger.debug(f"pagerank: {pagerank}")
        else:
            sitemap = domain_from_db.sitemap
            pagerank = domain_from_db.pagerank
            logger.debug("Pulling from database")
            logger.debug(f"sitemap: {sitemap}")
            logger.debug(f"pagerank: {pagerank}")

        return sitemap, pagerank

    def construct_url(self, url: str, path: str) -> str:
        "prepare url for use in sitemap"
        if not url.startswith("http"):
            url = "https://" + url

        return urljoin(url, path)

    def download_sitemap_if_exists(self, url) -> list:
        "get all possible sitemaps from the url"
        sitemap_collection = sitemap_tree_for_homepage(url)
        all_urls = list(set([page.url for page in sitemap_collection.all_pages()]))
        if not bool(all_urls):
            return None
        return all_urls

    def strip_url_to_homepage(self, url: str) -> str:
        """
        Strip URL to its homepage.

        :param url: URL to strip, e.g. "http://www.example.com/page.html".
        :return: Stripped homepage URL, e.g. "http://www.example.com/"
        """
        if not url:
            raise Exception("URL is empty.")

        try:
            uri = urlparse(url)
            assert uri.scheme, "Scheme must be set."
            assert uri.scheme.lower() in [
                "http",
                "https",
            ], "Scheme must be http:// or https://"
            uri = (
                uri.scheme,
                uri.netloc,
                "/",  # path
                "",  # params
                "",  # query
                "",  # fragment
            )
            url = urlunparse(uri)
        except Exception as ex:
            raise Exception("Unable to parse URL {}: {}".format(url, ex))

        return url

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

    def add_to_traverse_dict(self, url: str, traverse_dict: dict) -> None:
        "add url to traverse dict"
        # if url is not already in traverse dict, add it
        split = urlsplit(url)
        path = split.path
        if path not in traverse_dict:
            traverse_dict[path] = {"visited": False, "pagerank": 0}
        else:
            traverse_dict[path]["pagerank"] += 1
        return traverse_dict

    def build_ahref_traverse_dict(self, domain: str) -> dict:
        "generate sitemap for a given domain"
        # use crawler to generate sitemap
        path_traverse_dict = {"/": {"visited": False, "pagerank": 1}}
        while not all([v["visited"] for v in path_traverse_dict.values()]):
            paths_left_to_traverse = [
                path
                for path in path_traverse_dict.keys()
                if path_traverse_dict[path]["visited"] == False
            ]
            for path in paths_left_to_traverse:
                link_list = self.get_internal_ahref_links(domain, path)
                logging.debug(f"link_list: {link_list}")
                for link in link_list:
                    if self.check_if_url_is_internal_and_parsable(
                        domain=domain, url=link
                    ):
                        path_traverse_dict = self.add_to_traverse_dict(
                            link, path_traverse_dict
                        )
                path_traverse_dict[path]["visited"] = True
                logger.debug(f"traverse_dict: {path_traverse_dict}")
                logger.debug(f"paths left to traverse: {paths_left_to_traverse}")
        return path_traverse_dict

    def get_sitemap(self, traverse_dict: dict) -> list:
        "generate sitemap from traverse dict"
        return traverse_dict.keys()

    def get_pagerank(self, traverse_dict: dict) -> dict:
        "generate pagerank from traverse dict"
        return Counter(
            {path: value["pagerank"] for path, value in traverse_dict.items()}
        )

    def build_pagerank_from_sitemap(self, sitemap: list) -> dict:
        "generate pagerank from sitemap"
        pagerank = Counter()
        for url in sitemap:
            split = urlsplit(url)
            link_list = self.get_internal_ahref_links(
                domain=split.netloc, path=split.path
            )
            link_list_to_add = [
                link
                for link in link_list
                if self.check_if_url_is_internal_and_parsable(
                    domain=split.netloc, url=link
                )
            ]
            pagerank.update(link_list_to_add)

        return pagerank

    def download_html_save_to_db(self, domain: str, path: str) -> None:
        constructed_url = self.construct_url(domain, path)
        with get_db() as db:
            siteurl = crud.siteurl.get_by_url(db=db, url=constructed_url)
            if siteurl is None:
                html = requests.get(constructed_url).text
                obj_in = schemas.SiteUrlCreate(
                    domain=domain, url=constructed_url, html=html
                )
                crud.siteurl.create(db=db, obj_in=obj_in)
            else:
                html = crud.siteurl.get_by_url(db=db, url=constructed_url).html
        return html

    def get_internal_ahref_links(self, domain: str, path: str) -> list:
        "get all internal links from a given domain and path"
        html = self.download_html_save_to_db(domain=domain, path=path)
        soup = BeautifulSoup(html, "html.parser")
        list_of_links = [
            link.get("href") for link in soup.find_all("a") if link.get("href")
        ]
        return list_of_links

    def check_if_url_is_internal_and_parsable(self, domain: str, url: str) -> bool:
        "check if a url is internal to a given domain"
        skip_suffixes = {".pdf", ".jpg", ".png", ".jpeg", ".gif", ".svg"}
        split = urlsplit(url)
        if split.path.endswith(tuple(skip_suffixes)):
            return False
        if (
            not (split.netloc)
            and not (split.scheme)
            and split.path
            and split.path != "/"
        ):
            return True
        if split.netloc == domain:
            return True
        return False


if __name__ == "__main__":
    i = SitemapBuilder()
    print(
        i.strip_url_to_homepage(
            "https://www.google.com/search?q=mac+right+key+is+auto+pressed&oq=mac+right+key+is+auto+pressed&aqs=chrome..69i57.5952j0j1&sourceid=chrome&ie=UTF-8"
        )
    )
