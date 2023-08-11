import time
from functionality.extract import IndexEventPage

if __name__ == "__main__":
    home_url = input("Enter the home url: ")
    start_time = time.time()
    i = IndexEventPage(url_home=home_url)
    end_time = time.time()
    print(f"Time taken to build index: {end_time - start_time} seconds")
    print(f"Number of urls in sitemap: {len(i.sitemap)}")
    while True:
        print("-" * 50)
        site_url_text = input("Enter the url to get text from: ")
        print("-" * 50)
        print(i.db_get_text(site_url_text))
        print("-" * 50, end="\n\n")
