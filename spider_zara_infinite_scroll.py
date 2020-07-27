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
import sys
import time

class List_infinite_scroll_Spider(scrapy.Spider):
    name = "zara_infinite_scroll"
    __start_urls = ['https://www.zara.com/sg/en/woman-shoes-leather-l1275.html?v1=1180444','https://www.zara.com/sg/en/woman-shoes-flat-l1269.html?v1=1180338','https://www.zara.com/sg/en/woman-shoes-boots-ankle-boots-l1265.html?v1=1180540','https://www.zara.com/sg/en/woman-shoes-special-prices-l1290.html?v1=1180386','https://www.zara.com/sg/en/woman-shoes-sandals-flat-l1282.html?v1=1180331','https://www.zara.com/sg/en/woman-shoes-heeled-l1271.html?v1=1180339','https://www.zara.com/sg/en/woman-shoes-sandals-heeled-l1284.html?v1=1180335','https://www.zara.com/sg/en/woman-shoes-sneakers-l1287.html?v1=1180445','https://www.zara.com/sg/en/woman-shoes-party-l1278.html?v1=1180597','https://www.zara.com/kr/en/woman-shoes-party-l1278.html?v1=1180597','https://www.zara.com/kr/en/woman-shoes-white-l1682.html?v1=1180662','https://www.zara.com/kr/en/woman-shoes-leather-l1275.html?v1=1180444','https://www.zara.com/kr/en/woman-shoes-sneakers-l1287.html?v1=1180445','https://www.zara.com/kr/en/woman-shoes-sandals-heeled-l1284.html?v1=1180335','https://www.zara.com/kr/en/woman-shoes-heeled-l1271.html?v1=1180339','https://www.zara.com/kr/en/woman-shoes-sandals-flat-l1282.html?v1=1180331','https://www.zara.com/kr/en/woman-shoes-flat-l1269.html?v1=1180338','https://www.zara.com/kr/en/woman-shoes-boots-ankle-boots-l1265.html?v1=1180540','https://www.zara.com/kr/en/woman-shoes-special-prices-l1290.html?v1=1180386']
    download_delay = 1.5
    def start_requests(self):
        for url in self.__start_urls:
            download_delay = 1.5
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            request.meta['url'] = url
            download_delay = 1.5
            yield request

    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        download_delay = 1.5
        url = response.url
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        request = requests.get(url, headers = headers, timeout = 5)
        if request.status_code == 200:
            request = scrapy.Request(url = url, callback = self.parse_list_page)
            request.meta['url'] = response.meta['url']
            download_delay = 1.5
            yield request
     
        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req
     
    def extract_product(self, response):

     # Extract product list on the page 
        time.sleep(5)
        price = response.xpath('//*[@id="products"]//div/ul/li/div/div/div/span/@data-price').extract()
        links = response.xpath('//*[@id="products"]//div/ul/li/a/@href').extract()
        for dollar,url in zip(price,links):
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(
                url=url,
                callback=self.parse_product_page)
            request.meta['url'] = response.meta['url']
            request.meta['dollar'] = dollar
            download_delay = 1.5
            yield request
            
    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        time.sleep(5)
        secondary = response.xpath('//*[@id="product"]/div[3]/div/div[3]/div/h2/text()').extract()
        item = response.meta['url']
        location = re.search('www.zara.com/(.*)/en/woman', item).group(1)
        category =  re.search('woman-shoes-(.*).html?', item).group(1)
        color = response.xpath("//*[@id='product']/div/div/div/div/p/span/text()").extract()
        price = response.meta['dollar']
        title =  response.xpath('//div/div/div/header/h1/text()').extract()[0]
        size_range = response.xpath('//div/div/label/span/text()').extract()
        size_status = response.css("label ::text").getall()
        details = response.xpath("//*[@id='product']//div/div/div/div/div/p[1]/text()").extract()
        image = response.xpath("//div/div/div/a/@href").extract()

        yield{'Website': "Zara",
              "secondary": secondary,
            "title":title,
              "category": category,
              "location": location,
              "color": color,
              "size_range": size_range,
              "size_status": size_status,
              'price': price,
              'image': image,
               'details' : details,
                 }
        logging.info("processing " + response.url)
        yield None
        
