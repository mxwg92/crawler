from __future__ import print_function
import json
import re
from scrapy import Selector
from bs4 import BeautifulSoup
import logging
import requests
import scrapy
from scrapy.http.request import Request
import ast
from six.moves.urllib import parse
import pandas as pd
import os


class List_infinite_scroll_Spider(scrapy.Spider):
    name = "popsugar_infinite_scroll"
    __start_urls=["https://www.popsugar.com/latest/Heels?page=1",
                  "https://www.popsugar.com/latest/Sneakers?page=1",
                  "https://www.popsugar.com/latest/Sandals?page=1",
                  "https://www.popsugar.com/latest/Boots?page=1",
                  "https://www.popsugar.com/latest/Bags?page=1",
                  "https://www.popsugar.com/latest/Loafers?page=1"]
    
    def start_requests(self):
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            request.meta['url'] = url
            yield request

    def parse_list_page(self, response):
        """
        The url of next page is like
        https://scrapingclub.com/exercise/list_infinite_scroll/?page=2

        It can be found in a.next-page
        """
        
        if response.xpath('//*[@id="pager"]/span/a/@href').extract()!= []:
            if int(response.xpath('//*[@id="pager"]/span/a/@href').extract()[0][-1])<100:
                next_link =response.xpath('//*[@id="pager"]/span/a/@href').extract()[0]
                request = scrapy.Request(url=next_link,callback = self.parse_list_page)
                request.meta['url'] = response.meta['url']
                yield request

        # find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        
        
        links = response.xpath('//div[contains(@class, "ikb-post-container")]/div/div/a/@href').extract()
        for url in links:
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(
                url=url,
                callback=self.parse_product_page)

            request.meta['url'] = response.meta['url']
            yield request
    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        item  = response.meta['url']
        category = re.search('latest/(.*)?page=', item).group(1)
        title = response.xpath('//header/h2/span/text()').extract()
        date = response.xpath('//header/div/time/text()').extract()
        cat = response.xpath('//header/ul/li/a/span/text()').extract()
        topic = response.xpath('//div[contains(@class, "body-wrap")]//p/text()').extract()
        image =response.xpath('//div[contains(@class, "contents")]//a/img/@src').extract()

        yield{'Magazine':"Popsugar",
                'title': title,
              'date': date,
            'label': cat,
              'category': category,
              'image': image,
               'topic' : topic,

                 }
        logging.info("processing " + response.url)
        yield None