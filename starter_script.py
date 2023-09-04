import requests
import json
import urllib3
from functionality.rag_index import BuildRagIndex, QueryRagIndex
from urllib.parse import urlsplit, SplitResult

# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

f = open("data/sites_to_index.txt", "r")
domains = f.readlines()
domains = [x.strip("\n") for x in domains]
domains.insert(0, "https://www.autoevexpo.com/")

for domain in domains:
    urlsplit_obj = urlsplit(domain)
    b = QueryRagIndex(urlsplit_obj=urlsplit_obj)

# url = "http://35.200.180.141:8001/converse-website/"

# ses = requests.Session()
# ses.headers.update({"Content-Type": "application/json"})


# for domain in domains:
#     payload = json.dumps(
#         {
#             "domain": domain,
#             "query": "Give me a brief description of the event in a list form. Generate response in markdown.",
#         }
#     )

#     response = ses.get(url, data=payload)

#     with open("data/initial_index.log", "a") as d:
#         s = domain + "\n" + "-" * 30 + "\n" + response.text + "\n" + "-" * 30 + "\n"
#         d.write(s)
