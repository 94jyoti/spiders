from gencrawl.items.hospital.hospital_detail_item import HospitalDetailItem
from gencrawl.spiders.hospital.hospital_detail_spider import HospitalDetailSpider
from copy import deepcopy
from datetime import datetime
import re
from gencrawl.util.statics import Statics
import scrapy
import json
import copy
from scrapy.selector import Selector


class WmhwebComHospitalDetail(HospitalDetailSpider):
    name = 'hospital_detail_wmhweb_com_us'

    def get_items_or_req(self, response, default_item={}):

        items = self.prepare_items(response, default_item)
        meta = response.meta
        
        for item in items:
            if item['address_raw'] == []:
                item['address_raw']=(response.xpath("//h1/following::p[position()>=1][not(contains(.,'Medical School') or contains(.,'Residency')) ]").extract()[0]).replace(item['speciality'],"")
            if(item['address_raw'].replace("<p>","").startswith('Phone')):
                del item
                continue

            if("\xa0" in re.findall('<p>(.*?)</p>',item['address_raw'])):
                del item
                continue

            if("Phone" not in item['address_raw']):
                item['phone']=response.xpath("//p[contains(text(),'Phone')]//text()").extract()
                if(item['phone']==[]):
                    item['phone']= re.findall("\([\\d]{3}\)[\\d]{3}-[\\d]{4}",item['address_raw'].replace(" ",""))

            item['address_raw'] = item['address_raw'].replace("Phone", "").replace(":", "")
            if "practice_name" not in item.keys():
                temp_practice_name = response.xpath("//div[@class='art-postcontent clearfix']/p[1][not(contains(.,'Street'))]/text()").extract()
                if(item["speciality"] ==[]):
                    item['practice_name']=temp_practice_name
                elif(item['speciality']==temp_practice_name):
                    item['practice_name']=""
            temp_items=[]
            temp_items.append(item)
            other_address=response.xpath("//h1/following::p[position()=3][not(contains(.,'Medical School') or contains(.,'School') or contains(.,'College') or contains(.,'Phone') or contains(.,'Fellowship') or contains(.,'Residency'))]").extract()
            if(len(other_address)!=0):
                for c,i in enumerate(other_address):
                    temp_items.append(deepcopy(item))
                    temp_items[c+1]['address_raw']=i
            #print(item)
            if "practice_name" in item.keys():
                item['practice_name']=",".join(item['practice_name'])


        for item in temp_items:
            yield self.generate_item(item, HospitalDetailItem)