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
    name = "novo_au_infinite_scroll"
    
    __start_urls = [
                   'https://www.novoshoes.com.au/browse/lace-up-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/flat-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/ankle-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/sock-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/knee-high-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/heeled-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/leather-boots-p-1.html',
                   'https://www.novoshoes.com.au/browse/espadrilles-p-1.html',
                   'https://www.novoshoes.com.au/browse/pumps-p-1.html',
                   'https://www.novoshoes.com.au/browse/peep-toe-heels-p-1.html',
                   'https://www.novoshoes.com.au/browse/block-heels-p-1.html',
                   'https://www.novoshoes.com.au/browse/low-heels-p-1.html',
                   'https://www.novoshoes.com.au/browse/wedge-p-1.html',
                   'https://www.novoshoes.com.au/browse/party-p-1.html',
                   'https://www.novoshoes.com.au/browse/evening-shoes-p-1.html',
                   'https://www.novoshoes.com.au/browse/wedge-sandals-p-1.html',
                   'https://www.novoshoes.com.au/browse/flat-sandals-p-1.html',
                   'https://www.novoshoes.com.au/browse/espadrille-sandals-p-1.html',
                   'https://www.novoshoes.com.au/browse/lace-up-sandals-p-1.html',
                   'https://www.novoshoes.com.au/browse/leather-sandals-p-1.html',
                   'https://www.novoshoes.com.au/browse/flatforms-p-1.html',
                   'https://www.novoshoes.com.au/browse/casual-shoes-p-1.html',
                   'https://www.novoshoes.com.au/browse/womens-sneakers-p-1.html',
                   'https://www.novoshoes.com.au/browse/slide-shoes-p-1.html',
                   'https://www.novoshoes.com.au/browse/flats-p-1.html',
                   'https://www.novoshoes.com.au/browse/heels-p-1.html',
                   'https://www.novoshoes.com.au/browse/mules-p-1.html',
                   'https://www.novoshoes.com.au/browse/womens-corperate-shoes-p-1.html',
        
    ]

    
    def start_requests(self):
        
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            yield request

    def parse_list_page(self, response):
        
        #First, check if next page available, if found, yield request
        url = response.url
        number = re.search('-p-(.*).html', url).group(1)
        next_link =url[:url.find('-p-')] + '-p-'+ str(int(number)+24) + '.html'
        request = requests.get(next_link)
        if  request.status_code == 200 and request.url==response.url:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            yield request
        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        cat = re.search('browse/(.*)-p-', response.url).group(1)
        # Extract product list on the page 
        links = response.xpath('//*[@itemprop="itemListElement"]//article//h2/a/@href').extract()

        for url in links:
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(url=url,
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
        title = response.xpath('//*[contains(@class,"item-description")]/h1/text()').extract()
        desc = response.xpath('//span[contains(@class,"item-colour-note")]/text()').extract()
#         color_link = response.xpath("//div/div/ul[@class='color_list']/li/a/@href").extract()
        color_list = response.xpath('//select[contains(@name,"colour")]/option/text()').extract()
#         title2 = response.xpath("//div/form/div/div/p/span/text()").extract()[0]
        price = response.xpath('//*[contains(@id,"wdj-item-prices-div-page-wdg")]/script[2]/text()').extract()[0].split(',')
        size = response.xpath('//select[contains(@name,"size")]/option/text()').extract()[1:]
#         details = response.css("dd ::text").extract()
        image = response.xpath('//*[contains(@id,"wdj-item-image-gallery")]//a//img/@src').extract()

        yield{'Website': "novo",
            "title":title,
              "desc": desc,
#               "color_link": color_link,
              "color_list": color_list,
            'category': cat,
              'price': price,
              'image': image,
#                'details' : details,
                 }
        logging.info("processing " + response.url)
        yield None
        
