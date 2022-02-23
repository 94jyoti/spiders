from gencrawl.spiders.financial.financial_detail_spider import FinancialDetailSpider
from gencrawl.spiders.financial.financial_detail_field_mapping import FinancialDetailFieldMapSpider
import scrapy
import re


class BrookefieldfundsComDetail(FinancialDetailFieldMapSpider):
    name = 'financial_detail_brookefield_com'
    custom_settings = {
        "RETRY_TIMES": 5,
        "CRAWLERA_ENABLED": True,
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True
    }
    def get_items_or_req(self, response, default_item=None):
        items = super().get_items_or_req(response, default_item)
        file=open("brooookee.html","w")
        file.write(response.text)
        file.close()
        for item in items:
            try:
                item['share_inception_date']=response.xpath("//div[contains(@class,'key-stats-container key')]//p[contains(@class,'stat-value InceptionDate')]//span[contains(@class,'"+item['nasdaq_ticker']+"')]//text()").extract()[0]
            except:
                item['share_inception_date']=""
            item['sec_yield_30_day']=response.xpath("//div[contains(@class,'key-stats-container key')]//p[contains(@class,'ThirtyDaySECYieldSubsidized')]//span[contains(@class,'"+item['nasdaq_ticker']+"')]//text()").extract()[0]
            item['portfolio_assets']=response.xpath("//div[contains(@class,'key-stats-container key')]//p[contains(@class,'TotalNetAssets')]//span[contains(@class,'"+item['nasdaq_ticker']+"')]//text()").extract()[0]
            item['distribution_frequency']=response.xpath("//div[contains(@class,'key-stats-container key')]//p[contains(@class,'DistributionFrequency')]//span[contains(@class,'"+item['nasdaq_ticker']+"')]//text()").extract()[0]
            item['sec_yield_without_waivers_30_day']=response.xpath("//div[contains(@class,'key-stats-container key')]//p[contains(@class,'ThirtyDaySECYieldUnsubsidized')]//span[contains(@class,'"+item['nasdaq_ticker']+"')]//text()").extract()[0]
            try:
                item['total_net_assets']=response.xpath("//td[contains(text(),'Net assets')]//following-sibling::td//text()").extract()[0]+" "+response.xpath("//td[contains(text(),'Net assets')]//text()").extract()[0].split("(")[-1].replace(")","")
            except:
                item['total_net_assets'] = \
                response.xpath("//td[contains(text(),'Net Assets')]//following-sibling::td//text()").extract()[
                    0] + " " + response.xpath("//td[contains(text(),'Net Assets')]//text()").extract()[0].split("(")[
                    -1].replace(")", "")
            try:
                item['total_net_assets_date']=response.xpath("//p[contains(text(),'as of')]//text()").extract()[0].replace("as of","").replace("(","").replace(")","")
            except:
                pass
            benchmark=response.xpath("//p[contains(text(),'Class/Benchmark')]/following::text()[1][contains(.,'Index')]").extract()
            item['benchmarks']=list(set(benchmark))

            item['nasdaq_ticker']=''.join(i for i in item['nasdaq_ticker'] if not i.isdigit())
            try:
                gross_net=response.xpath("//p[contains(text(),'gross')]//text()").extract()[0].split("Class")
            except:
                gross_net=response.xpath("//strong[contains(text(),'gross')]//text()").extract()[0].split(";")[-1].split("Class")
            try:
                for iter in gross_net:
                        data=iter.split("and")
                        if(item['share_class'].replace("Class","") in iter):
                            for i in data:
                                if("gross" in i):
                                    item['total_expense_gross']=re.findall(r'\d*\.?\d+', i)[0]
                                if("net" in i):
                                    item['total_expense_net']=re.findall(r'\d*\.?\d+', i)[0]
            except:
                pass

            try:
                class_list=response.xpath("//ul[@class='distributionTabList']//li//a//text()").extract()
                class_list=[re.findall(r'\((.*?)\)',i)[0] for i in class_list]
                print(class_list)
                if(item['nasdaq_ticker'] in class_list):
                    index_ticker=class_list.index(item['nasdaq_ticker'])+1
                    #print(index_ticker)
                    table_data=response.xpath("//div[contains(@id,'distributions-tab-content-"+str(index_ticker)+"')]//tbody//tr")
                    #print("//div[contains(@id,'distributions-tab-content-"+str(index_ticker)+"')]//tbody//tr")
                    capital_gain_list=[]
                    dividends_list=[]
                    for row in table_data:
                        print("inside row")
                        print(row)
                        data_dict1 = {"ex_date": "", "pay_date": "", "ordinary_income": "", "qualified_income": "",
                                      "record_date": "", "per_share": "", "reinvestment_price": ""}
                        data_dict2 = {'long_term_per_share': "", 'cg_ex_date': "", 'cg_record_date': "", 'cg_pay_date': "",'short_term_per_share': "", 'total_per_share': "", 'cg_reinvestment_price': ""}
                        data_dict1['pay_date']=row.xpath(".//td[1]//text()").extract_first().replace("\n","")
                        print(data_dict1['pay_date'])
                        data_dict1['record_date']=row.xpath(".//td[2]//text()").extract_first()
                        data_dict1['ex_date']=row.xpath(".//td[3]//text()").extract_first()
                        data_dict1['per_share']=row.xpath(".//td[4]//text()").extract_first()
                        dividends_list.append(data_dict1)
                        #print(dividends_list)
                item['dividends']=dividends_list
            except:
                pass
            #for table in response.xpath("//div[contains(@class,'distributions-tab-content')]//table"):





        return items

