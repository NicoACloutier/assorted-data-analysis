import scrapy

class GovSpider(scrapy.Spider):
    name = "gov"

    def start_requests(self):
        self.start_urls = ['https://egypt.gov.eg/english/home.aspx',]
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = f'dumps\\file.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
