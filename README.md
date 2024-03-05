# Running the server

## How it Works

-   The app is an intelligent scraper that indexes and parses event pages from the internet. The parsed content is stored in a sqlite database, that is then further cleaned to extract high queality text that forms the basis of a RAG index. The RAG index is then used to retrieve relevant event pages, stuff that into the context window and then generate a response.. Currentyly the app is set up to use GPT-3.5 which is close to being deprecated so updating the llm to use GPT-4 will improve the quality of the responses.
-   Here is an [ flow chart / eraser diagram of the app ](https://app.eraser.io/workspace/MQuiGCRkaVbxYrhFhFqD?origin=share)
    ![eraser diagram](https://app.eraser.io/workspace/MQuiGCRkaVbxYrhFhFqD?origin=share)
-   When you make a request, the app will first check if the domain is indexed. If it is, it will use the RAG index to retrieve relevant event pages. If it is not, it will start a new indexing process. The indexing process is a multi stage process that involves downloading the sitemap, parsing the sitemap, and then parsing the event pages. The parsed content is then stored in a sqlite database. The RAG index is then used to retrieve relevant event pages, stuff that into the context window and then generate a response.

# Instructions to run and use

## Status

`/converse-website` is the main endpoint that works
`/converse` is the endpoint that utilizes past messages as context history, that needs firther work to complete

## Run the app the first time

Note: This is a one time process. The app will be ready to run after this. Do not run this after if you have ever run this before.

-   git clone the repo
    `git clone https://github.com/anudeep22003/eventgpt.git`
-   enter working directory `cd eventgpt`
-   give execution privileges to the initialize script
    `chmod +x initialize.sh`
-   Then run `sh ./initialize.sh`

## Run the app

from root directory run
`sh ./run.sh`

# Modifying for your usecase

## Modifying sql tables

Context: You want to add functionality by adding new tables, and related orm classes

-   Models
    -   Add new tables in `app/models/<name-your-table>.py`, make sure to `from base_class import Base`
    -   Add the new python file you created to `app/models/__init__.py` (this is what alembic uses to recognize that new tables were added and autogenerates revisions)
-   Schemas
    -   Add corresponding pydantic tables in `app/schemas/<name-your-schema>.py` also import the relevant parts into `schemas/__init__.py`
-   CRUD
    -   Add `app/crud/<name-of-model>.py` and make sure the CRUD class inherits `CRUDBase`
    -   create an instance of the class and import into `app/crud/__init__.py`

## Using Alembic

Context: You have made changes to the sql database. Eg: Added models, schemas, or changed the existing models and schemas

1. Generate the migration script
    - Add changes models to `models/__init__.py`. This ensures that alembic can access the new models
    - run `alembic revision --autogenerate -m "<enter change message here>"` this will generate a migratiin script in versions
    - Look through the files and make sure that changes are correct. Reference for detected and non detected changes [here](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
2. Running the migration
    - `alembic upgrade head`
3. Upgrading and downgrading
    - go to specific version by mentioning the identifier `alembic upgrade ae1` (also supports partial identifiers)
    - Relative identifiers `alembic upgrade +2` or `alembic downgrade -1`

## Open Tasks

-   [ ] Implement recursive text splitter
-   [ ] Implement reranker
-   [ ] import exploding tags in Beautiful Soup
-   [ ] implement multistage retreival
-   [ ] Implement date retreiver using Marvin

# Parsing tasks

-   [ ] While creating vector index skip pages that have less than threshold number of characters
-   [ ] After parse, check if content in pages is same
-   [ ] Check if the link redirects to a different page, and only add that page to sitemap (create a redirect map?)
-   [ ] Handle https://interfoamvietnam.com/en/ here the event page is a subdomain of the main website
-   [ ] Handle cases where the event page is undera subdomain of a larger company wevbsite. Eg: `www.google.com/events/GSOC` all relevant links are daughters
-   [ ] Index only event pages, not post pages (how do you differentiate?)
-   [ ] For genera;ized parsign handle the following cases:
-   [ ] `#nav-on` or other `#` based links because they point internal
-   [ ] `https://www.medica.de` and `https://www.medica.de/` as different pages

## Indexing tasks

-   [ ] Skip pages that have no content in them or match another page exactly
-   [ ] Skip pages that have less than threshold number of characters

## RAG Accuracy tasks

-   [ ] Add evaluation metrics for RAG
-   [ ] Achieve current capability parity with an external class
-   [ ] Add logic to skip indexes with barely any content

## Completed Tasks

-   [x] Handle sources that are paths not links
-   [x] Is not working with new url it has never seen or downloaded (eg: https://www.saudifoodexpo.com/)
-   [x] Rewriting the index and erasing the prev one
-   [x] Capture the right sources, currently doc_ids are being stored in sources.`needs to get better, recursive tree`
-   [x] Create sitemap even if it doesnt exist using pagerank
-   [x] Ensure that if a domain not indexed is passed, then a new indexing starts
-   [x] To keep complexity low we will index only the first 20 pages. Ended up with a more intelligent solve where we keep the highest pagerank websites.
-   [x] Generalized parsing case to handle: links pointing outward `facebook.com` for example.
-   [x] Is unable to build a new index if a domain isn't already indexed. Returns an emppty response. Look at `QueryRagIndex`
