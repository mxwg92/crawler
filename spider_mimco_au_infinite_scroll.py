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

class List_infinite_scroll_Spider(scrapy.Spider):
    name = "mimco_au_infinite_scroll"
    __start_urls = [
'https://www.mimco-accessories.com/shop/shoes/boots[1].htm?&&serveas=ajax',
                    'https://www.mimco-accessories.com/shop/shoes/flats[1].htm?&&serveas=ajax',
                   'https://www.mimco-accessories.com/shop/shoes/heels[1].htm?&&serveas=ajax',
                    'https://www.mimco-accessories.com/shop/shoes/sandals[1].htm?&&serveas=ajax',
                   'https://www.mimco-accessories.com/shop/shoes/sneakers[1].htm?&&serveas=ajax',
    ]


    
    def start_requests(self):
        
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            yield request

    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        url = response.url
        number=re.search(r"\[([A-Za-z0-9_]+)\]", url).group(1)
        next_link = url[:url.find('[')] + '['+ str(int(number)+1) + '].htm?&&serveas=ajax'
        request = requests.get(next_link, timeout = 5)
        if request.status_code == 200 and response.xpath('//body/div/section//h2/a/@href').extract()!=[]:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['cat'] = re.search('/shoes/(.*)\[', next_link).group(1)
            yield request

        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        cat=re.search('/shoes/(.*)\[', response.url).group(1)
        # Extract product list on the page 
        links = response.xpath('//body/div/section//h2/a/@href').extract()
        for url in links:
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(
                url=url,
                callback=self.parse_product_page)
            request.meta['cat'] = cat
            request.meta['url'] = url
            yield request
            

    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        item  = response.meta["url"]
        cat = response.meta["cat"]
        title = response.xpath('//h1[@itemprop="name"]/text()').extract()
        desc = response.xpath('//div[@class="content long_description"]/text()').extract()
#         color_link = response.xpath("//div/div/ul[@class='color_list']/li/a/@href").extract()
        color_list = response.xpath('//li[@class="colour"]//label/text()').extract()
#         title2 = response.xpath("//div/form/div/div/p/span/text()").extract()[0]
        price = response.xpath('//span[@itemprop="price"]/text()').extract()
        size = response.xpath('//*[@id="sizes_colourway_70"]/option/text()').extract()
#         details = response.css("dd ::text").extract()
        image = response.xpath('//figure//a/img/@src').extract()

        yield{'Website': "mimco",
            "title":title,
#               "title2": title2,
              "desc": desc,
#               "color_link": color_link,
              "color_list": color_list,
              "size": size,
            'category': cat,
              'price': price,
              'image': image,
#                'details' : details,
                 }
        logging.info("processing " + response.url)
        yield None
        
