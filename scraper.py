import re
import requests
import utils
from bs4 import BeautifulSoup
import time
import math
import concurrent.futures
import json
import random
import pandas as pd
from fake_useragent import UserAgent
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class AmazonProductReviewScraper:

    user_agent = UserAgent()

    def __init__(self,base_url:str):
        self.reviews = {"date":[],"username":[],"review_title":[],"review_content":[],"rating":[]}
        self.url = "/".join(base_url.split("/")[0:3]) + "/dp/product-reviews/" + base_url.split("/")[5] + "?pageNumber={}"
        self.page_range = (1,self.request(url = self.url.format(1),user_agent = AmazonProductReviewScraper.user_agent.random,return_n_pages=True))
    
    def scrape_all_pages_concurrent(self,max_workers = 15):
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futs = []
            for url in [self.url.format(x) for x in range(1,self.page_range[1])]:
                futs.append(executor.submit(AmazonProductReviewScraper.request, url=url,user_agent = AmazonProductReviewScraper.user_agent.random))
            
            results = [x.result() for x in futs]     
            output_dict =  {     
            "date":[],
            "username":[],
            "review_title":[],
            "review_content":[],
            "rating":[]
            }
            for key in output_dict:
                for i in range(len(results)):
                    output_dict[key].extend(results[i][key])

            end = time.time()
            print(f"{round(end-start,2)} seconds.")

            self.scrape_result_ = output_dict

            return output_dict

    @staticmethod
    def request(url,user_agent,return_n_pages = False):

        while True:

            response = requests.get(url, verify=False, headers={'User-Agent': user_agent}, proxies= random.choice(utils.get_amazon_countries_dict()))
            total_attempts = 30

            if not response.ok:
                raise Exception(response.raise_for_status())

            if "api-services-support@amazon.com" in response.text:
                if not total_attempts:
                    raise ConnectionError("Unable to bypass captcha.")

                time.sleep(1)
                total_attempts-=1
                continue

            break

        soup = BeautifulSoup(response.content,"lxml")

        return AmazonProductReviewScraper._parse(soup) if not return_n_pages else AmazonProductReviewScraper._get_total_pages(soup)
    

    @classmethod
    def _parse(cls,html:BeautifulSoup):

        reviews = html.findAll("div", {"class":"a-section review aok-relative"})
        reviews = BeautifulSoup('<br/>'.join([str(tag) for tag in reviews]), 'html.parser')
        titles = [x.find("span").get_text() if x.find("span") is not None else " " for x in reviews.find_all("a", {"data-hook":"review-title"}) + reviews.find_all("span", {"data-hook":"review-title"})]
        names = [x.contents[0] if len(x.contents) else " " for x in reviews.find_all("span",{"class":"a-profile-name"})]
        ratings = [float(x.get_text().split(" ")[0]) if len(x.contents)  else " " for x in reviews.find_all("i",{"data-hook":"review-star-rating"}) + reviews.find_all("i",{"data-hook":"cmps-review-star-rating"})]
        dates = [x.contents[0] if len(x.contents) else " " for x in reviews.find_all("span",{"data-hook":"review-date"})]
        contents = [re.sub(r"\s+|\\n"," ", x.find("span").get_text("\n").strip()) if x.find("span") is not None else " " for x in reviews.find_all("span", {"data-hook":"review-body"})]


        return {
            "date":[x.split("on")[1].strip() if "on" in x else None for x in dates],
            "username":names,
            "review_title":titles,
            "review_content":contents,
            "rating":ratings
        }
        
    @classmethod
    def _get_total_pages(cls,html:BeautifulSoup):
        sep = re.compile(r"[,.]")
        tag = html.find("span",{"class":"a-size-base a-color-secondary"})
        n_reviews = int(sep.sub("",tag.contents[0].split(" ")[0].strip()))
        total_pages = math.ceil(n_reviews/10)
        print(f"{total_pages} pages.")
        return total_pages
    
    def to_csv(self,file_name):
        if not hasattr(self,"scrape_result_"):
            raise NotImplementedError("No data scraped.")
        file_name = file_name if re.search(r".csv",file_name) else file_name + ".csv"

        frame = pd.DataFrame(self.scrape_result_)
        frame["date"] = pd.to_datetime(frame["date"])
        frame.to_csv(file_name,encoding="utf-16",index=False)
    
    def to_json(self,file_name):
        if not hasattr(self,"scrape_result_"):
            raise NotImplementedError("No data scraped.")
        file_name = file_name if re.search(r".json",file_name) else file_name + ".json"

        with open(file_name,"w",encoding="utf-16") as handle:
            json.dump(self.scrape_result_,handle)