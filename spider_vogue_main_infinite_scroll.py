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
    
    name = "vogue_main_infinite_scroll"
    
    __start_urls=["https://www.vogue.co.uk/xhr/search?q=sandals&page=1",
                  "https://www.vogue.co.uk/xhr/topic/sneakers?list_counter=1&page=1&shift=0",
                  "https://www.vogue.co.uk/xhr/topic/heels?list_counter=1&page=1&shift=0", 
                  "https://www.vogue.co.uk/xhr/topic/loafers?list_counter=1&page=1&shift=0"]
    
    def start_requests(self):
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            request.meta['url'] = url
            yield request

    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        url=response.url
        number = json.loads(response.text)['data']['local_storage'][1]['value']
        next_link="page="+str(number)+ "&shift=0"
        next_link = url[:url.find('page=')] + next_link
        request = requests.get(next_link)
        if request.status_code == 200:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['url'] = response.meta['url']
            yield request

        # find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        
        links = response.xpath("//li/article/a/@href").extract()
        for url in links:
            url=url[2:-2]+"/"
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse((result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request=Request(url=url,callback=self.parse_product_page)
            request.meta['url'] = response.meta['url']
            yield request

    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        item  = response.meta['url']
        category = re.search('/search?q=(.*)?&page=', item).group(1)
        title = response.xpath("//h1/text()").extract()
        label = response.xpath("//header/div/div/div/a/text()").extract()
        date = response.xpath("//div[contains(@class,'a-header__date')]/text()").extract()
        topic = response.css('p.bb-p ::text').getall()
        image =  response.xpath("//div/div/div/figure/div/img/@data-src").extract()

        yield{'Magazine':"Vogue",
                'title': title,
                'label': label,
              'category': category,
              'date': date,
              'image': image,
               'topic' : topic,

                 }


        logging.info("processing " + response.url)
        yield None