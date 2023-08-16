# Running the server

## Critical Bugs

- [ ] Is not working with new url it has never seen or downloaded (eg: https://www.saudifoodexpo.com/)
- [ ] Rewriting the index and erasing the prev one

## Tasks

- [ ] Handle cases where the event page is undera subdomain of a larger company wevbsite. Eg: `www.google.com/events/GSOC` all relevant links are daughters
- [-] Capture the right sources, currently doc_ids are being stored in sources.`needs to get better, recursive tree`
- [x] Create sitemap even if it doesnt exist using pagerank
- [ ] Ensure that if a domain not indexed is passed, then a new indexing starts
- [ ] To keep complexity low we will index only the first 20 pages
- [ ] Index only event pages, not post pages (how do you differentiate?)

## Open Bugs:

- [ ] Is unable to build a new index if a domain isn't already indexed. Returns an emppty response. Look at `QueryRagIndex`

from root directory run
`sh ./run.sh`

# Modifying for your usecase

## Modifying sql tables

Context: You want to add functionality by adding new tables, and related orm classes

- Models
  - Add new tables in `app/models/<name-your-table>.py`, make sure to `from base_class import Base`
  - Add the new python file you created to `app/models/__init__.py` (this is what alembic uses to recognize that new tables were added and autogenerates revisions)
- Schemas
  - Add corresponding pydantic tables in `app/schemas/<name-your-schema>.py` also import the relevant parts into `schemas/__init__.py`
- CRUD
  - Add `app/crud/<name-of-model>.py` and make sure the CRUD class inherits `CRUDBase`
  - create an instance of the class and import into `app/crud/__init__.py`

## Using Alembic

Context: You have made changes to the sql database. Eg: Added models, schemas, or changed the existing models and schemas

1. Generate the migration script
   - Add changes models to `models/__init__.py`. This ensures that alembic can access the new models
   - run `alembic revision --autogenerate -m "<enter change message here>"` this will generate a migratiin script in versions
   - Look through the files and make sure that changes are correct. Reference for detected and non detected changes [here](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
2. Running the migration
   - `alembic upgrade head`
3. Upgrading and downgradinf
   - go to specific version by mentioning the identifier `alembic upgrade ae1` (also supports partial identifiers)
   - Relative identifiers `alembic upgrade +2` or `alembic downgrade -1`
