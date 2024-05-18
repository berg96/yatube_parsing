from typing import Iterable

import scrapy
from scrapy import Request


class YatubeSpider(scrapy.Spider):
    name = "yatube"
    allowed_domains = ["51.250.32.185"]
    start_urls = ["https://51.250.32.185/"]
    login_url = 'http://51.250.32.185/login/'

    def start_requests(self):
        yield scrapy.Request(self.login_url, callback=self.login)

    def login(self, response):
        token = response.css(
            'input[name="csrfmiddlewaretoken"]::attr(value)'
        ).get()
        return [
            scrapy.FormRequest(
                self.login_url,
                formdata={
                    'username': 'test_parser_user',
                    'password': 'testpassword',
                    'csrfmiddlewaretoken': token,
                },
                callback=self.parse,
            )
        ]

    def parse(self, response):
        for card in response.css('div.card'):
            yield {
                'author': card.css('strong.d-block::text').get(),
                'text': ' '.join(
                    t.strip() for t in card.css('p.card-text::text').getall()
                ).strip(),
                'date': card.css('small.text-muted::text').get()
            }
        next_page = response.css(
            'li.page-item a:contains("Следующая")::attr(href)'
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
