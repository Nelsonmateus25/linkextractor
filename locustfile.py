from locust import HttpUser, task, between
from urllib.parse import quote

TEST_URLS = [
    "https://en.wikipedia.org/wiki/Special:AllPages",
    "https://httpbin.org/links/1000/1",
    "https://crawler-test.com",
    "https://github.com/apache",
    "https://arxiv.org/list/cs/recent",
    "https://linuxtracker.org/",
    "https://wordpress.org/plugins/",
    "https://news.ycombinator.com/news?p=1",
    "https://en.wikipedia.org/wiki/Index_of_computing_articles",
    "https://www.iana.org/domains/reserved"
]


class LinkExtractorUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task
    def extract_links_sequence(self):
        for url in TEST_URLS:
            encoded_url = quote(url, safe="")

            with self.client.get(
                f"/api/{encoded_url}",
                name="/api/[url]",
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"HTTP {response.status_code}")