"""
Script de teste de carga para o serviço Link Extractor.

Uso:
    # Com interface web (modo interativo):
    locust -f locustfile.py --host http://localhost:4567

    # Modo headless (automatizado), com exportação CSV:
    locust -f locustfile.py \
        --host http://localhost:4567 \
        --users 10 \
        --spawn-rate 2 \
        --run-time 60s \
        --headless \
        --csv resultados/ruby_cache_10u

Substitua o host por:
    - http://localhost:4567  → API Ruby
    - http://localhost:5000  → API Python
"""

from locust import HttpUser, task, between

# 10 URLs públicas e estáveis para os testes
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
    """
    Usuário virtual que realiza 10 invocações sequenciais ao serviço de
    extração de links, passando uma URL diferente a cada invocação.
    """

    wait_time = between(0.5, 2.0)

    @task
    def extract_links_sequence(self):
        for url in TEST_URLS:
            with self.client.get(
                f"/api/{url}",
                name="/api/[url]",
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"HTTP {response.status_code}")
