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
    name = "wmag_infinite_scroll"
    __start_urls=["https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=shoes","https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=sneakers","https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=heels","https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=loafers","https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=sandals", "https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=bags","https://www.wmagazine.com/api/search?page=1&size=10&sort=score%20desc&types=article%2Cgallery%2Cvideo&q=boots"]
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
        url=response.url
        parsed_data = json.loads(response.text)
        next_link =url[:url.find('page=')] + "page="+str(parsed_data['query']['page']+1) +url[url.find('&size=10'):]
        request = requests.get(next_link)

        
        if request.status_code == 200 and len(parsed_data['items'])!=0:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['url'] = response.meta['url']
            yield request

        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        
        parsed_data = json.loads(response.text)
        links=[]
        for item in parsed_data["items"]:
            links.append(item['url'])
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
        category = re.search('2Cvideo&q=(.*)', item).group(1)
        title = response.xpath("//div/div/div/div/h1/text()").extract()
        date = response.xpath("//div/div/div/div/time/text()").extract()
        cat = response.xpath("//div/div/div/div/span/text()").extract()
        topic = response.css('p ::text').getall()
        topic = topic[:topic.index('Keywords')]
        image = response.xpath("//picture/img/@src").extract()

        yield{'Magazine':"Wmag",
                'title': title[0],
              'date': date[0],
            'label': cat,
              'category': category,
              'image': image,
               'topic' : topic,

                 }
        logging.info("processing " + response.url)
        yield None