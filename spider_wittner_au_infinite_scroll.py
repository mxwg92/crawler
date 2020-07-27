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
    name = "wittner_au_infinite_scroll"
    __start_urls = ['https://www.wittner.com.au/shoes/ankleboots.html','https://www.wittner.com.au/shoes/heels.html',
                   'https://www.wittner.com.au/shoes/long-boots.html','https://www.wittner.com.au/shoes/pumps.html',
                   'https://www.wittner.com.au/shoes/flats.html','https://www.wittner.com.au/shoes/wedges.html',
                   'https://www.wittner.com.au/shoes/sandals.html','https://www.wittner.com.au/shoes/slides.html',
                   'https://www.wittner.com.au/shoes/corporate.html','https://www.wittner.com.au/shoes/espadrilles.html',
                   'https://www.wittner.com.au/shoes/loafers.html']


    
    def start_requests(self):
        
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
#             request.meta['url'] = url
            request.meta['cat'] = url[:-5].split('/')[-1]
            yield request

    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        url = response.url
        number = response.xpath('//*[@id="product-listing-area"]/div[2]/div[1]/div[2]/div[3]/span/text()').extract()[0].split(" ")[1]
        if len(url.split('/'))>5:
            next_link = url[:-6] + str(int(number)+1) + '.html'
        else:
            next_link = url[:-5] + "/page/" + str(int(number)+1) + '.html'
        request = requests.get(next_link, timeout = 5)
        if request.status_code == 200:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['cat'] = re.search('/shoes/(.*)/page', next_link).group(1)
            yield request

        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        
        # Extract product list on the page 
        links = response.xpath('//ul/li/div/a/@href').extract()
        for url in links:
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(
                url=url,
                callback=self.parse_product_page)
            request.meta['cat'] = response.meta['cat']
            request.meta['url'] = url
            yield request
            

    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        item  = response.meta["url"]
        cat = response.meta["cat"]
        title = response.xpath('//*[@id="product_addtocart_form"]/div/h1/text()').extract()[0]
        desc = response.xpath('//*[@id="product-tabs"]/div/div/div/text()').extract()[0]
#         color_link = response.xpath("//div/div/ul[@class='color_list']/li/a/@href").extract()
        color_list =response.xpath('//ul[contains(@id,"attributegrid-color")]/li/a/img/@alt').extract()
#         title2 = response.xpath("//div/form/div/div/p/span/text()").extract()[0]
        price = response.xpath('//form//div/div/span[contains(@id,"product-price")]/span/text()').extract()
#         size = response.xpath("//div[@class='size_list size']/a").extract()
#         details = response.css("dd ::text").extract()
        image = response.xpath('//div/div/div[1]/div/a/img/@src').extract()

        yield{'Website': "Wittner",
            "title":title,
#               "title2": title2,
              "desc": desc,
#               "color_link": color_link,
              "color_list": color_list,
#               "size": size,
            'category': cat,
              'price': price,
              'image': image,
#                'details' : details,
                 }
        logging.info("processing " + response.url)
        yield None
        
