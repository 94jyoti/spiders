from gencrawl.spiders.financial.financial_detail_spider import FinancialDetailSpider
from gencrawl.util.statics import Statics
import json
import scrapy
from gencrawl.items.financial.financial_detail_item import FinancialDetailItem
from gencrawl.spiders.financial.financial_detail_field_mapping import FinancialDetailFieldMapSpider

from datetime import datetime
import datetime
import urllib.parse
import re
from gencrawl.util.statics import Statics
# import urllib
import itertools
import requests
from lxml import html
from scrapy.selector import Selector
import copy
import ast


class fpaFundsDetail(FinancialDetailFieldMapSpider):
    name = 'fpafunds_com'

    def get_items_or_req(self, response, default_item={}):
        items = super().get_items_or_req(response, default_item)
        meta = response.meta
        meta['items'] = items
        selector = scrapy.Selector(text=response.text, type="html")
        share_classes = selector.xpath("//select[@id='shareClassPicker']/option/text()").getall()
        if response.url[-1]!="/":
            url = response.url + "/"
        
        fund_url = url.split("/")[-2]

        meta['fund_url'] = fund_url
        meta['share_class'] = selector.xpath("//th[contains(text(),'Share Class')]/following-sibling::td/span/text()").get()
        yield scrapy.Request("https://fpa.com/funds/performance/"+fund_url,callback=self.benchmarks,
                             dont_filter=True,meta=meta)

    def benchmarks(self, response):
        meta = response.meta
        selector = scrapy.Selector(text=response.text, type="html")
        benchmarks = selector.xpath("(//th[contains(text(),'Fund/Index')]//ancestor::table)[1]//tr/td[1]/text()").getall()
        benchmarks = [b.strip() for b in benchmarks]
        meta['benchmarks'] = benchmarks[1:]
        yield scrapy.Request("https://fpa.com/funds/portfolio-characteristics/"+meta['fund_url'],callback=self.portfolio_characteristics,dont_filter=True,meta=meta)

    def portfolio_characteristics(self,response):
        meta= response.meta
        selector = scrapy.Selector(text=response.text, type="html")
        eff_maturity_date = selector.xpath(
            "//h2[contains(text(),'Portfolio Structure')]/following-sibling::div//strong/text()").get().split('of')[-1].strip()
        data_blocks = selector.xpath("//div[@class='data-container']/@data-data").getall()
        xx = data_blocks[1]
        x = ast.literal_eval(xx)
        eff_maturity = ''
        for i in x:
            for j in i['items']:
                if j['key']=='EFF. Maturity':
                    eff_maturity = j['val']
                if j['key']=='EFF. Duration':
                    eff_duration = j['val']

        for i in meta['items']:
            i['benchmarks'] = meta['benchmarks']
            if len(eff_maturity)>0:
                i['average_weighted_maturity'] = eff_maturity
                i['effective_duration'] = eff_duration
                i['average_weighted_maturity_as_of_date'] = eff_maturity_date
                i['effective_duration_date'] = eff_maturity_date

            if not 'share_class' in list(i.keys()):
                print("hhh:",i['instrument_name'])
                #share_class = selector.xpath("//th[contains(text(),'Share Class')]/following-sibling::td/span/text()").get()
                i['share_class'] = meta['share_class']
            yield self.generate_item(i, FinancialDetailItem)



       






    