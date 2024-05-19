import scrapy


class GroupSpider(scrapy.Spider):
    name = "group"
    allowed_domains = ["51.250.32.185"]
    start_urls = ["http://51.250.32.185/"]
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
        all_groups = response.css('a.group_link::attr(href)')
        for group_link in all_groups:
            yield response.follow(group_link, callback=self.parse_group)
        next_page = response.css(
            'li.page-item a:contains("Следующая")::attr(href)'
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_group(self, response):
        card = response.css('div.card')
        yield {
            'group_name': card.css('h2::text').get(),
            'description': card.css('p.group_descr::text').get(),
            'posts_count': int(card.css(
                'div.posts_count::text'
            ).get().strip().split(' ')[1])
        }

