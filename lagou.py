
from selenium import webdriver
from lxml import etree
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pymysql
import csv


class LagouSpider(object):
    driver_path = r"C:\Users\hj\Anaconda3\chromedriver.exe"

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=LagouSpider.driver_path)
        
        # 拉勾网：深圳站-Python
        # self.url = 'https://www.lagou.com/jobs/list_python?city=%E6%B7%B1%E5%9C%B3&cl=true&fromSearch=true&labelWords=&suginput='
        
        # 拉勾网：深圳站-外贸专员
        self.url = 'https://www.lagou.com/jobs/list_%E5%A4%96%E8%B4%B8%E4%B8%9A%E5%8A%A1%E5%91%98?city=%E6%B7%B1%E5%9C%B3&cl=false&fromSearch=true&labelWords=&suginput='
        self.positions = []

    def run(self):
        self.driver.get(self.url)
        while True:
            source = self.driver.page_source
            WebDriverWait(driver=self.driver,timeout=10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='pager_container']/span[last()]"))
            )
            self.parse_list_page(source)
            try:
                next_btn = self.driver.find_element_by_xpath("//div[@class='pager_container']/span[last()]")
                if "pager_next_disabled" in next_btn.get_attribute("class"):
                    break
                else:
                    next_btn.click()
            except:
                print(source)

            time.sleep(1)

    def parse_list_page(self,source):
        html = etree.HTML(source)
        links = html.xpath("//a[@class='position_link']/@href")
        for link in links:
            self.request_detail_page(link)
            time.sleep(1)

    def request_detail_page(self,url):
        # self.driver.get(url)
        # print()
        # print(url)
        # print()
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver,timeout=10).until(
            EC.presence_of_element_located((By.XPATH,"//div[@class='job-name']/span[@class='name']"))
        )
        source = self.driver.page_source
        self.parse_detail_page(source)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self,source):
        html = etree.HTML(source)
        position_name = html.xpath("//span[@class='name']/text()")[0]
        job_request_spans = html.xpath("//dd[@class='job_request']//span")

        salary = job_request_spans[0].xpath('.//text()')[0].strip()
        # city = job_request_spans[1].xpath(".//text()")[0].strip()
        # city = re.sub(r"[\s/]", "", city)

        # 地址
        address = html.xpath('//*[@id="job_detail"]/dd[3]/div[1]/a[2]//text()')[0].strip()

        # address2 = html.xpath('//*[@id="job_detail"]/dd[3]/div[1]/a[3]//text()')[0].strip()

        # 工作年限/经验
        work_years = job_request_spans[2].xpath(".//text()")[0].strip()
        work_years = re.sub(r"[\s/]", "", work_years)

        # 学历
        education = job_request_spans[3].xpath(".//text()")[0].strip()
        education = re.sub(r"[\s/]", "", education)

        # 描述
        description = "".join(html.xpath("//dd[@class='job_bt']//text()")).strip()
        # company_name = html.xpath("//h2[@class='f1']/text()")

        # 公司名字
        company_name = html.xpath('/html/body/div[2]/div/div[1]/div/div[1]//text()')[0]
        position = {
            'position_name': position_name,
            'company_name': company_name,
            'salary': salary,
            'address': address,
            # 'address2': address2,
            'work_years': work_years,
            'education': education,
            'description': description
        }
        self.positions.append(position)
        print(position)
        self.save(position)
        

    def save(self, position):
        """存储到 MySQL"""
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='abcd110139', db='test')
        print('连接数据库成功')
        cursor = db.cursor()

        table = 'dt2'     # 数据表
        fields = ', '.join(position.keys())
        values = ', '.join(['%s'] * len(position))
        # print(position.keys())
        # print(position.values())
        print(tuple(position.values()))

        sql = 'insert into {table}({fields}) VALUES ({values})'.format(table=table, fields=fields, values=values)

        try:
            if cursor.execute(sql, tuple(position.values())):
                print('插入成功')
                db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            db.close()

if __name__ == '__main__':
    spider = LagouSpider()
    spider.run()
