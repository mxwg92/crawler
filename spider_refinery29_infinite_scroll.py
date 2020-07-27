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
    
    name = "refinery29_infinite_scroll"
    
    __start_urls=[
                  "https://www.refinery29.com/en-us/search?q=sneakers&json=false&page=1",
                  "https://www.refinery29.com/en-us/search?q=heels&json=false&page=1",
                  "https://www.refinery29.com/en-us/search?q=sandals&json=false&page=1",
                  "https://www.refinery29.com/en-us/search?q=loafers&json=false&page=1",
                    "https://www.refinery29.com/en-us/search?q=shoes&json=false&page=1",
                  "https://www.refinery29.com/en-us/search?q=bags&json=false&page=1"]
    
    def start_requests(self):
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            request.meta['url'] = url
            yield request

    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        number = int(re.search('page=(.*)', response.url).group(1))+1
        if len(response.xpath('//*[@id="more-stories"]/button/span/text()').extract())>0 and number<100:
            next_link = re.search('(.*)page=', response.url).group(1)+"page="+str(number+1)
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['url'] = response.meta['url']
            yield request

        # find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        links = response.xpath('//*[@id="below-the-fold-modules"]/div/div/div/div/div/div/div/a/@href').extract()
        for url in links:
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", "")
            )
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
        category = re.search('q=(.*)&json', item).group(1)
        title = response.xpath('//*[@id="r29-container"]/div/article/div/div/h1/text()').extract()
        tag =  response.xpath('//*[@id="r29-container"]/div/article/div/a/span/span/span/text()').extract()
        date = re.search('datePublished":"(.*)Z","d',response.xpath('/html/head/script').extract()[7]).group(1)
        topic = response.css('div.r29-article.right-rail-article ::text').getall()
        image =  [ i for i in response.xpath('/html/head/script').extract() if "jpg" in i]

        yield{'Magazine':"refinery29",
                'title': title,
                'tag': tag,
              'category': category,
              'date': date,
              'image': image,
               'topic' : topic,

                 }


        logging.info("processing " + response.url)
        yield None