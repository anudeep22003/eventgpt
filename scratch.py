import time
from functionality.extract import IndexEventPage, check_if_domain_exists
from functionality.rag_index import BuildRagIndex

if __name__ == "__main__":
    while True:
        home_url = input("Enter the home url: ")
        if check_if_domain_exists(home_url):
            print("Domain already indexed, continuing...")
            pass
        else:
            start_time = time.time()
            i = IndexEventPage(url_home=home_url)
            end_time = time.time()
            print(f"Time taken to build index: {end_time - start_time} seconds")
            print(f"Number of urls in sitemap: {len(i.sitemap)}")

        b = BuildRagIndex(domain=home_url)
        query_engine = b.query_rag_index

        user_in = ""
        while user_in != "q":
            user_in = input(
                "Enter 'text' to retreive text\nEnter 'query' to get answer\nEnter 'q' to quit: "
            )
            while user_in == "text":
                site_url_text = input("Enter the url to get text from: ")
                if site_url_text == "q":
                    break
                print("-" * 50)
                print("-" * 50)
                print(i.db_get_text(site_url_text))
                print("-" * 50, end="\n\n")
                user_in = input("Enter query: ")
            while user_in == "query":
                query = input("Enter query: ")
                if query == "q":
                    break
                print("-" * 50)
                print("-" * 20, " response ", "-" * 20)
                response = query_engine(query)
                print("Response", str(response), end="\n\n")
                print("-" * 20, " sources ", "-" * 20)
                print("Sources", response.get_formatted_sources())
                print("-" * 50)
