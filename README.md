# Running the server

## Open Tasks

- [ ] Handle https://interfoamvietnam.com/en/ here the event page is a subdomain of the main website
- [ ] Handle cases where the event page is undera subdomain of a larger company wevbsite. Eg: `www.google.com/events/GSOC` all relevant links are daughters
- [ ] Is unable to build a new index if a domain isn't already indexed. Returns an emppty response. Look at `QueryRagIndex`
- [ ] Index only event pages, not post pages (how do you differentiate?)
- [ ] For genera;ized parsign handle the following cases:
- [ ] `#nav-on` or other `#` based links because they point internal
- [ ] `https://www.medica.de` and `https://www.medica.de/` as different pages
- [ ] links pointing outward `facebook.com` for example.
      link*list: ['#nav-on', 'https://www.medica.de', 'https://www.medica.de', '/de/Home/Hot_topic_trends', '/de/Home/Hilfe_Anreise', '/de/Home/Hilfe_Anreise/Kontakt', '/de/Home/Hilfe_Anreise/Internationale_Vertretungen/Übersicht', '/de/Home/Hilfe_Anreise/Anreise', '/de/Home/Hilfe_Anreise/Unterkunft_CityInfos', '/de/Home/Hilfe_Anreise/FAQ/FAQ', '/de/Ausstellen', '/de/Ausstellen/Aussteller_werden', '/de/Ausstellen/Aussteller_werden/Online-Anmeldung', '/de/Ausstellen/Aussteller_werden/Standflächen-Kostenrechner', '/de/Ausstellen/Aussteller_werden/Messeschwerpunkte', '/de/Ausstellen/Aussteller_werden/Messevorbereitung', '/de/Ausstellen/Informationen', '/de/Ausstellen/Informationen/Ansprechpartner', '/de/Ausstellen/Informationen/Download_Center', '/de/Ausstellen/Informationen/Daten_Fakten', '/de/Ausstellen/Informationen/Service-ABC', 'https://www.medica.de/de/Home/Hilfe_Anreise/Unterkunft_CityInfos', 'https://standbau.messe-duesseldorf.de/cgi-bin/md_sb/lib/pub/tt.cgi?oid=1768&lang=1&ticket=g_u_e_s_t', '/de/Ausstellen/Services', '/de/Ausstellen/Services/Online-Order-System*(OOS)', '/de/Ausstellen/Services/Ausstellerprofil', '/de/Ausstellen/Services/Aussteller-Dashboard/Dashboard-Startseite', '/de/Ausstellen/Services/Ausstellerausweise/Ausstellerausweise', '/de/Ausstellen/Services/Gutscheine/Besuchergutscheine*So_funktioniert_s', '/de/Ausstellen/Services/Scan2Lead', '/de/Ausstellen/Services/Logos_Banner', '/de/Ausstellen/Messeauftritt', 'https://www.messe-duesseldorf.de/de/Gel%C3%A4nde_Services/Service_Alliance/Service_Alliance', '/de/Ausstellen/Messeauftritt/Marketing', '/de/Ausstellen/Messeauftritt/Presse', '/de/Ausstellen/Messeauftritt/Dienstleistungen', '/de/Besuchen', '/de/Besuchen/Das_erwartet_Sie', '/de/Besuchen/Das_erwartet_Sie/Gründe_für_Ihren_Besuch', 'https://www.medica.de/vis/v1/de/search?f_type=profile&_query=', 'https://www.medica.de/konferenzen_foren', '/de/Besuchen/Das_erwartet_Sie/Download_Center', '/de/Besuchen/Vorbereitung', '/de/Besuchen/Vorbereitung/Tickets_Gutscheine', '/de/Besuchen/Vorbereitung/Hallen-\_Geländepläne', '/de/Besuchen/Vorbereitung/Öffnungszeiten', 'https://www.medica.de/de/Hilfe_Anreise/Anreise', '/de/Besuchen/Vorbereitung/MyOrganizer', '/de/Besuchen/Vorbereitung/MEDICA_App_Social_Media', '/de/Besuchen/Services', '/de/Besuchen/Services/Gastro_Guide', '/de/Besuchen/Services/Digitaler_Pressestand', '/de/Besuchen/Services/Eigene_Tour_planen', 'https://www.medica.de/de/Media_News/Erlebniswelten', '/de/Aussteller_Produkte/Alle_Aussteller_Produkte_2023/Ausstellersuche', '/de/Aussteller_Produkte/Alle_Aussteller_Produkte_2023/Ausstellersuche', '/de/Aussteller_Produkte/Produktkategorien/Produktkategorien', '/hallenplan?lang=1&ticket=g_u_e_s_t&oid=85465', '/de/Aussteller_Produkte/World_wide_exhibitor_map', '/de/Programm', '/de/Programm/Foren', '/de/Programm/Foren/MEDICA_CONNECTED_HEALTHCARE_FORUM', '/de/Programm/Foren/MEDICA_HEALTH_IT_FORUM', '/de/Programm/Foren/MEDICA_LABMED_FORUM', '/de/Programm/Foren/MEDICA_ECON_FORUM_by_TK', '/de/Programm/Foren/MEDICA_TECH_FORUM', 'http://www.compamed.de/high_tech_forum_ivam1', 'http://www.compamed.de/suppliers_forum_devicemed1', '/de/Programm/Konferenzen', '/de/Programm/Konferenzen/Deutscher_Krankenhaustag', '/de/Programm/Konferenzen/MEDICA_MEDICINE_SPORTS_CONFERENCE', '/de/Programm/Konferenzen/DiMiMED*-_International_Conference_on_Disaster_and_Military_Medicine', '/de/Programm/Sonderschauen_mehr', '/de/Programm/Sonderschauen_mehr/MEDICA_START-UP_PARK', 'https://www.medica.de/de/Programm/Foren/MEDICA_CONNECTED_HEALTHCARE_FORUM/MEDICA_START-UP_COMPETITION', '/de/Programm/Sonderschauen_mehr/MEDICA_SPORTS_HUB', '/de/Programm/Sonderschauen_mehr/WT_|\_WEARABLE_TECHNOLOGIES_SHOW', 'https://germanmedicalaward.com', '/de/Media_News', '/de/Media_News/Presse', '/de/Media_News/Presse/Presseservices', '/de/Media_News/Presse/Pressematerial', '/de/Media_News/Presse/Digitaler_Pressestand', '/de/Media_News/News', '/de/Media_News/News/Ausstellernews', '/de/Media_News/News/Branchennews', '/de/Media_News/News/Trendthemen', 'https://www.medica.de/de/Media_News/Erlebniswelten-Magazin/Newsletter_abonnieren', '/de/Media_News/Erlebniswelten-Magazin', '/de/medtech-devices/home', '/de/digital-health/home', '/de/lab-diagnostics/home', '/de/physio-tech/home', '/de/disposables/home', '/de/medica-deep-dive', '/de/medtech-devices/robots-or-flexible-precise-tireless-medica-deep-dive', '/de/digital-health/ai-diagnostics-imaging-trustworthy-companion-medica-deep-dive', '/de/digital-health/sensors-collecting-data-monitoring-diagnostics-medica-deep-dive', '/de/digital-health/telemedicine-remote-treatment-improve-care-medica-deep-dive', 'https://www.MEDICAlliance.global', 'https://www.medica.de', '/de/Media_News', '/de/Media_News/Erlebniswelten-Magazin', '/de/medtech-devices/home', '/de/medtech-devices/news-home', '/vis/v1/de/search?ticket=g_u_e_s_t&\_query=&f_type=profile&f_prod=medcom2023.MEDICA.01.02', '/vis/v1/de/search?ticket=g_u_e_s_t&\_query=&f_type=profile&f_prod=medcom2023.MEDICA.01.02.02', '/vis/v1/de/search?ticket=g_u_e_s_t&\_query=&f_type=profile&f_prod=medcom2023.MEDICA.01.02.03', '/vis/v1/de/search?ticket=g_u_e_s_t&\_query=&f_type=profile&f_prod=medcom2023.MEDICA.06', '/vis/v1/de/search?ticket=g_u_e_s_t&\_query=&f_type=profile&f_prod=medcom2023.MEDICA.06.06.05', '/de/medtech-devices/MRT_KI_Krankenhaus-Koeln-Porz', '/de/medtech-devices/Gehirnkartierung_präoperative_Planung_mit_funktioneller_MRT', '/de/medtech-devices/magdeburg-forschungsinfrastruktur-bildgestützte-hirnforschung', 'http://www.oth-aw.de ', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=7791', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=7823', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=27929', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=8253', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=7814', '/de/medtech-devices/Sichere-MRT-Untersuchungen-trotz-Implantaten?mcat_id=12522', '/de/medtech-devices/Leitlinie-Intensivstation', '/de/medtech-devices/Leitlinie-Intensivstation', '/de/medtech-devices/KI-diagnostiziert-Schlaganfall', '/de/medtech-devices/KI-diagnostiziert-Schlaganfall', '/de/medtech-devices/Hirntumore-dank-innovativer-Bildgebund-und-KI-exakt-bestrahlen', '/de/medtech-devices/Hirntumore-dank-innovativer-Bildgebund-und-KI-exakt-bestrahlen', '/de/medtech-devices/Neue-Netzwerke-im-Gehirn-entdeckt', '/de/medtech-devices/Neue-Netzwerke-im-Gehirn-entdeckt', '#', 'https://www.facebook.com/MEDICADuesseldorf', 'https://twitter.com/MEDICATradeFair', 'https://de.linkedin.com/showcase/medica-international-trade-fair', 'http://www.youtube.com/user/MEDICATradeFair', '/de/Ausstellen/Aussteller_werden/Online-Anmeldung', 'https://shop.messe-duesseldorf.de/medcom_regi_d', '/de/Media_News/Erlebniswelten-Magazin/Newsletter_abonnieren', '/vis/v1/de/catalogue', ' https://shop.messe-duesseldorf.de/medcom_shop_d ', 'https://www.medica.de/de/Hilfe_Anreise/Kontakt', 'https://www.medica.de/de/Hilfe_Anreise/Internationale_Vertretungen/%C3%9Cbersicht', 'https://www.medica.de/de/Hilfe_Anreise/FAQ/FAQ', 'https://www.medicalliance.global/', 'https://www.medica.de/', 'https://www.compamed.de/', 'https://www.rehacare.de/', 'https://www.famdent.com/', 'https://www.medicalfair-asia.com/', 'https://medicalfairbrasil.com.br/', 'https://www.medicalfair.cn/', 'https://www.medicalfair-india.com/', 'https://www.medicalfair-thailand.com/', 'https://www.medmanufacturing-asia.com/', 'https://feriameditech.com/', 'https://www.rehacare-shanghai.com/en/', 'https://www.messe-duesseldorf.de', 'https://www.duesseldorfcongress.de/', 'https://www.forum-gesundheitswirtschaft.com/', 'https://www.messe-duesseldorf.de', '/Privacy_policy_1', '/impressum_1', '#', '/compliance_1', '/contact_1', 'https://enable-javascript.com/de']

## Completed Tasks

- [x] Handle sources that are paths not links
- [x] Is not working with new url it has never seen or downloaded (eg: https://www.saudifoodexpo.com/)
- [x] Rewriting the index and erasing the prev one
- [x] Capture the right sources, currently doc_ids are being stored in sources.`needs to get better, recursive tree`
- [x] Create sitemap even if it doesnt exist using pagerank
- [x] Ensure that if a domain not indexed is passed, then a new indexing starts
- [x] To keep complexity low we will index only the first 20 pages. Ended up with a more intelligent solve where we keep the highest pagerank websites.

# Instructions to run and use

## Run the app the first time

Note: This is a one time process. The app will be ready to run after this. Do not run this after if you have ever run this before.

- git clone the repo
  `git clone https://github.com/anudeep22003/eventgpt.git`
- enter working directory `cd eventgpt`
- give execution privileges to the initialize script
  `chmod +x initialize.sh`
- Then run `sh ./initialize.sh`

## Run the app

## Run the app

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
3. Upgrading and downgrading
   - go to specific version by mentioning the identifier `alembic upgrade ae1` (also supports partial identifiers)
   - Relative identifiers `alembic upgrade +2` or `alembic downgrade -1`
