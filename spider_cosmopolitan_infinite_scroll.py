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

class List_infinite_scroll_Spider(scrapy.Spider):
    
    name = "cosmo_infinite_scroll"
    
    __start_urls = ["https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22handbags%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=","https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22shoes%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=",
                 "https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22sneakers%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=","https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22heels%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=","https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22sandals%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=","https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22boots%22%2C%22page_size%22%3A42%7D&page=1&cachebuster=","https://www.cosmopolitan.com/ajax/infiniteload/?id=search&class=CoreModels%5Csearch%5CTagQueryModel&viewset=search&trackingId=search-results&trackingLabel=handbags&params=%7B%22input%22%3A%22loafers%22%2C%22page_size%22%3A42%7D&page=1&cachebuster="]
    
    def start_requests(self):
        for url in self.__start_urls:
            request = scrapy.Request(url,
            callback = self.parse_list_page)
            request.meta['url'] = url
            yield request
            

    def parse_list_page(self, response):

        #First, check if next page available, if found, yield request
        url=response.url
        number = int(ast.literal_eval(response.xpath ("//body/div/@data-params").get())['params']['page']) + 1
        next_link =  str(number) + "&cachebuster="
        next_link = url[:url.find('page=')] + next_link
        request = requests.get(next_link)
        
        if request.status_code == 200:
            request = scrapy.Request(url=next_link,callback = self.parse_list_page)
            request.meta['url'] = response.meta['url']
            yield request

        #Find product link and yield request back
        for req in self.extract_product(response):
            yield req

    def extract_product(self, response):
        
        # Extract product list on the page 
        links = response.xpath("//a[contains(@class,'simple-item-image')]/@href").extract()
        label = response.xpath("/html/body/div/div/div/a/text()").extract()
        for index, url in enumerate(links):
            result = parse.urlparse(response.url)
            base_url = parse.urlunparse(
                (result.scheme, result.netloc, "", "", "", ""))
            url = parse.urljoin(base_url, url)
            request = Request(
                url=url,
                callback=self.parse_product_page)
            request.meta['label'] = label[index]
            request.meta['url'] = response.meta['url']
            yield request
            
    def parse_product_page(self, response):
        """
        The product page use ajax to get the data, try to analyze it and finish it
        by yourself.
        """
        label = response.meta['label']
        item  = response.meta['url']
        category = re.search('%22%3A%22(.*)%22%2C%22', item).group(1)
        title = response.xpath("//h1/text()").extract()
        date = response.xpath("//div[contains(@class,'content-info')]//time[contains(@class,'content-info-date')]/text()").extract()[0].strip()
        topic = response.css('p ::text').getall()
        image = response.xpath("//picture[contains(@class,'lazyimage')]/img/@data-src").extract()
              
        yield{'Magazine': "Cosmopolitan",
                'title': title,
              'category': category,
              'date': date,
              'image': image,
               'topic' : topic,
              'label' : label,
                 }

        logging.info("processing " + response.url)
        yield None