import requests
import json
import re
from urllib.parse import urlparse
import openai
import time
from bs4 import BeautifulSoup
from collections import Counter
from usp.tree import sitemap_tree_for_homepage
from sqlalchemy.orm import Session
from functools import wraps
from functionality.sitemap import SitemapBuilder

from app import models, schemas, crud, db
from app.deps import get_db


def check_if_domain_exists(url: str) -> bool:
    "check if domain exists in the database"
    domain = urlparse(url).netloc
    with get_db() as db:
        domain_from_db = crud.domain.get_domain_by_name(db=db, domain=domain)
    if domain_from_db is None:
        return False
    return True


class IndexLoad:
    def __init__(self, url_home: str, freq_limit: int) -> None:
        self.url_home = url_home
        self.sitemap = self.get_sitemap(url_home)
        self.textrank = Counter()
        self.pagerank = Counter()
        self.page_index = {}
        self.freq_limit = freq_limit


class IndexEventPage:
    def __init__(self, url_home: str, freq_limit: int = 4) -> None:
        self.url_home = url_home
        self.sitemap = self.get_sitemap(url_home)
        self.textrank = Counter()
        self.pagerank = Counter()
        self.page_index = {}
        self.freq_limit = freq_limit
        self.orchestrator()
        pass

    ######################################################
    ################ Utility Functions ################
    ######################################################

    def timer(func) -> None:
        "time the function"

        @wraps(func)
        def wrap_func(self, *args, **kwargs):
            start_time = time.time()
            results = func(self, *args, **kwargs)
            end_time = time.time()
            print(f"Time taken for {func.__name__}: {end_time - start_time} seconds")
            return results

        return wrap_func

    ######################################################

    def change_freq_limit(self, new_freq_limit: int) -> None:
        self.freq_limit = new_freq_limit

    def check_if_event_is_parsed(self) -> bool:
        "check is to load from db, or to perform a new parse"
        ...

    ##################################################
    ################ Domain Functions ################
    ###################################################

    @timer
    def get_sitemap(self, url: str) -> list[str]:
        # "get all possible sitemaps from the url"
        # sitemap_collection = sitemap_tree_for_homepage(url)
        # all_urls = list(set([page.url for page in sitemap_collection.all_pages()]))
        # if not bool(all_urls):
        #     return None
        s = SitemapBuilder()
        sitemap, _ = s(url)
        return sitemap

    def construct_sitemap(self):
        "if sitemap does not exist, construct using internal ahref links"
        ...

    def save_sitemap(self):
        "save extracted sitemap to the db"
        ...

    def url_importance_scorer(self, url: str) -> int:
        """Generates an importance score, between 1-3
        - If link is internal then high importance
        - if link is external then low importance
        - If link is high in the pagerank then middle importance

        Args:
            url (str): The url whose imprtance needs to be checked

        Returns:
            int: score between 1-3, higher means more important
        """
        ...

    def freshness_checker(self) -> list[str]:
        "check if any pages have been updated, if yes append to refresh list"
        ...

    def save_html_to_db(self, html_text: str | None):
        "take the downloaded html_text and save it to disk for later comparison"
        "how will you save this in the database?"
        ...

    def create_index(self) -> list[dict, dict]:
        "returns a forward and a backward index of the documents and sources"
        ...

    ###################################################
    ################ SiteUrl Functions ################
    ###################################################

    def orchestrator(self) -> None:
        "orchestrates the entire process of indexing"
        self.download_html_build_ranks()
        self.db_create_domain_entry(domain=urlparse(self.url_home).netloc)
        self.extract_clean_text()

    @timer
    def download_html_build_ranks(self) -> None:
        for url in self.sitemap:
            # if already exists in db, then get from db
            with get_db() as db:
                siteurl = crud.siteurl.get_by_url(db=db, url=url)
                if siteurl is None:
                    html_text = self.get_html_text(url)
                else:
                    html_text = siteurl.html
                soup = self.build_soup(html_text)
                self.build_ranks(soup)
                # save html content to db?
                # make siteurl db entry for each url
                if siteurl is None:
                    self.db_create_siteurl_entry(url=url, html=html_text)

    @timer
    def extract_clean_text(self) -> str:
        "extract for every url ranked text and save it to db"
        for url in self.sitemap:
            self.parse_html_store_db(url)

    def db_create_siteurl_entry(self, url: str, html: str = "", text: str = "") -> None:
        "create a siteurl entry in the database"
        #! assumes url_home is the homepage, user may pass a random page
        #! saving the entire url including path
        domain = urlparse(self.url_home).netloc
        siteurl = schemas.SiteUrlCreate(url=url, domain=domain, text=text, html=html)
        with get_db() as db:
            # db = get_db()
            siteurl_from_db = crud.siteurl.create(db=db, obj_in=siteurl)
        return siteurl_from_db

    def get_html_text(self, url: str) -> str:
        "download the html of the page"
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        else:
            return """
                <!DOCTYPE html>
                <html lang="en">
                <body>
                    None
                </body>
                </html>
            """

    def build_soup(self, html_text: str) -> BeautifulSoup:
        "build a soup object from the html text"
        return BeautifulSoup(html_text, "html.parser")

    def build_ranks(self, soup: BeautifulSoup) -> None:
        "add to both textrank and pagerank"
        # build pagrank
        for link in soup.find_all("a"):
            self.pagerank.update([link.get("href")])

        # build textrank
        for string in soup.stripped_strings:
            newline_removed = re.sub("\n+", " ", string)
            whitespace_removed = re.sub("\s+", " ", newline_removed)
            self.textrank.update([str(whitespace_removed)])

    def ranked_parse(self, soup: BeautifulSoup) -> str:
        "parse the html using textrank"
        ranked = []
        limit = self.freq_limit
        for string in soup.stripped_strings:
            if self.textrank[string] <= limit:
                if soup.find(re.compile("^h"), string=string):
                    ranked.append(f"\n\n{string}:\n")
                elif soup.find(re.compile("^li"), string=string):
                    ranked.append(f"- {string}")
                else:
                    ranked.append(string)

        return "\n".join(ranked)

    def parse_html_store_db(self, url) -> str:
        """
        Use textrank frequency mapping to parse high informational content
        Load the html from sqlite, rather than downloading again if it exists
        #! not performing any checks if the domain being investigated is indexed or not
        #! do you even need to perform above check?
        """
        with get_db() as db:
            # db = get_db()
            siteurl = crud.siteurl.get_by_url(db=db, url=url)
        #! i think the below check is unnecessary
        if siteurl is None:
            html_text = self.get_html_text(url)
            siteurl = self.db_create_siteurl_entry(url=url, html=html_text)
        else:
            html_text = siteurl.html
        soup = self.build_soup(html_text)
        text = self.ranked_parse(soup)
        with get_db() as db:
            siteurl = crud.siteurl.update_text(db=db, url=url, text=text)

    def db_get_text(self, url: str) -> str:
        #! handle not finding the entry and getting None
        with get_db() as db:
            # db = get_db()
            siteurl = crud.siteurl.get_by_url(db=db, url=url)
        return siteurl.text

    ######################################################
    ################ EndofIndex Functions ################
    ######################################################

    def db_create_domain_entry(self, domain: str) -> models.Domain:
        "create a domain entry in the database"
        pagerank = self.pagerank
        textrank = self.textrank
        sitemap = " , ".join(self.sitemap)

        domain = schemas.DomainCreate(
            domain=domain,
            pagerank=pagerank,
            textrank=textrank,
            sitemap=sitemap,
        )
        with get_db() as db:
            # db = get_db()
            domain_from_db = crud.domain.create(db=db, obj_in=domain)
        return domain_from_db


if __name__ == "__main__":
    home_url = input("Enter the home url: ")
    start_time = time.time()
    i = IndexEventPage(url_home=home_url)
    end_time = time.time()
    print(f"Time taken to build index: {end_time - start_time} seconds")
    print(f"Number of urls in sitemap: {len(i.sitemap)}")
    while True:
        print("-" * 50)
        site_url_text = input("Enter the url to parse: ")
        print("-" * 50)
        print(i.parse_html(site_url_text))
        print("-" * 50, end="\n\n")
