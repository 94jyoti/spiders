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
import logging
import requests
from lxml import html
from scrapy.selector import Selector
import copy
from html import unescape
import re
import ast
class harvestglobalDetail(FinancialDetailSpider):
    #logging.basicConfig(filename="hsbc.log", level=logging.INFO)
    #logging.info("InvestorFundsUSHSBCDetail")
    name = 'harvestglobal_us'
    custom_settings = {
        "HTTPCACHE_ENABLED": False,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DOWNLOAD_DELAY": 4,
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
        "CRAWLERA_ENABLED":True
    }
    def start_requests(self):
        for i, obj in enumerate(self.input):
            url = obj[self.url_key]
            static_url = "https://www.harvestglobal.us/hgi/index.php/funds/card-view"
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
            }
            cookies = {
            "csrfToken": "Do0mgauZEkxokVU5v2qvoUBC",
            "locale": "en-us",
            "ReVisit": "1",
            "ReVisit.sig": "diKwuv56Y8_d-cnspTaQsOXwOKiRC3y4IxgEDzaDfvk",
            "disclaimerAccept": "1",
            "disclaimerAccept.sig": "5nREFp1DGBSZ3xpWV6xryB0kw5AJzzsnJA-bS9iM1uE"
            }
            yield scrapy.Request(static_url, headers=headers,cookies=cookies, method="GET", callback=self.make_request,dont_filter=True)
    def make_request(self, response):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
            }
        cookies = {
        "csrfToken": "Do0mgauZEkxokVU5v2qvoUBC",
        "locale": "en-us",
        "ReVisit": "1",
        "ReVisit.sig": "diKwuv56Y8_d-cnspTaQsOXwOKiRC3y4IxgEDzaDfvk",
        "disclaimerAccept": "1",
        "disclaimerAccept.sig": "5nREFp1DGBSZ3xpWV6xryB0kw5AJzzsnJA-bS9iM1uE"
        }
        static_url = 'https://www.harvestglobal.us/hgi/index.php/funds/active/HXIIX'
        yield scrapy.Request(static_url, headers=headers,cookies=cookies, method="GET", callback=self.make_request2,dont_filter=True)
    def make_request2(self,response):
        items = self.prepare_items(response)
        selector = scrapy.Selector(text=response.text, type="html")
        ticker = selector.xpath("//div[@id='page-container']/div").get()
        unescaped = unescape(response.text)
        temp_block = selector.xpath("//div[@class='row-fluid']/@ng-init").get()
        x = temp_block[9:].replace(";setting.performaceChartTitleMap = {activeAssertNavTitle:'Price Chart',passiveAssertNavTitle:'Last Closing NAV Per Unit',closePricesTitle:'Market Closing Price',asof:'as of'}",'')
        x = x.replace('true',"")
        xx = re.search('\"fund_cate_info\":(.*),\"fundAnnualList\"', temp_block).group(1)
        portfolio_consultant = re.search('\"investment_advisor\":\"(.*)\",\"base_currency\"', temp_block).group(1)
        print("portfolio_consultant:",portfolio_consultant)
        res = ast.literal_eval(xx)
        items[0]['portfolio_consultant']=portfolio_consultant
        items[0]['investment_objective'] ='The Harvest Asian Bond Fund seeks long-term return through a combination of capital appreciation and current income.'
        items[0]['investment_strategy']='The Fund seeks to achieve its objective by investing, under normal market conditions, at least 80% of its net assets in a portfolio of fixed income securities of Asian issuers, and other instruments with economic characteristics similar to such securities..'
        items[0]['instrument_name'] = 'Harvest Asian Bond Fund'
        temp_items=[]
        for r in res:
            item_copy = copy.deepcopy(items)
            item_copy[0]['share_class'] = r['currency_subdivide']
            item_copy[0]['nasdaq_ticker'] = r['bloomberg_ticker']
            item_copy[0]['isin'] = r['ISIN_code']
            item_copy[0]['total_expense_gross'] = r['gross_expense_ratio']
            item_copy[0]['total_expense_net'] = r['net_expense_ratio']
            item_copy[0]['minimum_initial_investment'] = r['minimum_investment']
            print(item_copy[0])
            temp_items.append(item_copy[0])
            #yield self.generate_item(item_copy[0], FinancialDetailItem)
        print(temp_items)
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
        }
        cookies = {
        "csrfToken": "Do0mgauZEkxokVU5v2qvoUBC",
        "locale": "en-us",
        "ReVisit": "1",
        "ReVisit.sig": "diKwuv56Y8_d-cnspTaQsOXwOKiRC3y4IxgEDzaDfvk",
        "disclaimerAccept": "1",
        "disclaimerAccept.sig": "5nREFp1DGBSZ3xpWV6xryB0kw5AJzzsnJA-bS9iM1uE"
        }
        meta = response.meta
        meta['items'] = temp_items
        static_url = 'https://www.harvestglobal.us/hgi/index.php/funds/active/HXIIX#distributions'
        yield scrapy.Request(static_url,meta=meta, headers=headers, cookies=cookies, method="GET",callback=self.make_request3, dont_filter=True)
    def make_request3(self, response):
        #items = self.prepare_items(response)
        meta=response.meta
        items=meta['items']
        #items = response.meta['items']
        print("itemsmsmsmsm",items)
        selector = scrapy.Selector(text=response.text, type="html")
        print("here")
        open('harvest.html','w',encoding='utf-8').write(response.text)
        data=re.findall('<div class="row-fluid" ng-controller="DetailController" ng-init="initData=(.*?)>',response.text)
        data = data[0].replace("&lt", "").replace("&gt", "").replace("&quot;", "").replace("&#39","")
        final_data = re.findall('{fundType:active.*?,fundDividend:(.*?),dictionary:{fund_type_info:{USRF:{_id:5b5850df36a9f169477b25a7.*?" ',data)[0]
        #final_data = final_data.split("{")
        #final_data.remove[final_data[0]]
        #final_data.remove[final_data[0]]
        final_data = final_data.split("fund_code:HXIIX")
        print(final_data)
        print(len(final_data))
        final_data.remove(final_data[0])

        for item in items:
            #break
            for data in final_data:
                if(item['share_class'] in data):
                    dividend_list=[]
                    dict=data.split("{")
                    dict.remove(dict[0])
                    for i in dict:
                        data_dict1 = {"ex_date": "", "pay_date": "", "ordinary_income": "", "qualified_income": "",
                                      "record_date": "", "per_share": "", "reinvestment_price": ""}
                        distribution=i.split(",")
                        print(distribution)
                        for j in distribution:
                            print(j)
                            if("ex_dividend_date" in j):
                                data_dict1['ex_date'] = j.split(":")[-1]

                            if("payment_date" in j):
                                data_dict1['pay_date']=j.split(":")[-1]
                            if("distribution_per_unit" in j):
                                data_dict1['per_share']=j.split(":")[-1].replace("}","")
                            if("record_date" in j):
                                data_dict1['record_date']=j.split(":")[-1]

                        dividend_list.append(data_dict1)
                        #break
                        
                        print(dividend_list)
                        #break
            item['dividends']=dividend_list
            yield self.generate_item(item, FinancialDetailItem)



















