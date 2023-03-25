
# -*- coding: utf-8 -*-
import time

import pymysql
import xlrd
import xlutils.copy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool as ThreadPool
from selenium.common.exceptions import NoSuchElementException


def connectDB():
    host = "127.0.0.1"
    dbName = "crwal_gov"
    user = "root"
    password = "925303"
    # 此处添加charset='utf8'是为了在数据库中显示中文，此编码必须与数据库的编码一致
    db = pymysql.connect(host, user, password, dbName, charset='utf8')
    return db
    cursorDB = db.cursor()
    return cursorDB


def inserttable(item_name, budget_amount, admin_name, website_list):
    insertContentSql = "INSERT INTO tj" + "(item_name,budget_amount,admin_name,website_list)VALUES(%s,%s,%s,%s)"
    DB_insert = connectDB()
    cursor_insert = DB_insert.cursor()
    cursor_insert.execute(insertContentSql, (item_name, budget_amount, admin_name, website_list))
    DB_insert.commit()
    DB_insert.close()


def sub_crawler(website_list):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头chrome 不打开浏览器进行模拟点击
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get(website_list)
    time.sleep(0.5)
    print(website_list)  # 检错

    try:
        item_name = driver.find_element_by_xpath(
            "//*[@id='detail']/div[2]/div/div[2]/div/div[2]/table/tbody/tr[2]/td[2]").text
        budget_amount = driver.find_element_by_xpath(
            "//*[@id='detail']/div[2]/div/div[2]/div/div[2]/table/tbody/tr[11]/td[2]").text
        admin_name = driver.find_element_by_xpath(
            "//*[@id='detail']/div[2]/div/div[2]/div/div[2]/table/tbody/tr[4]/td[2]").text

        inserttable(item_name, budget_amount, admin_name, website_list)

        print("已爬取{}\n".format(item_name))

    except NoSuchElementException as msg:
        print("已爬取{}\n{}\n".format("异常版面，需手动标注", website_list))

    driver.quit()


def crawler(url, threadNum):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头chrome
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get(url)

    # 开始爬信息 (第一页)
    website_list = [elemente.get_attribute("href") for elemente in
                    driver.find_elements_by_css_selector("a[style='line-height:18px']")]
    time.sleep(0.8)
    # 剩余页 爬信息
    print(len(website_list))  # 爬到的信息条数
    driver.quit()
    pool = ThreadPool(processes=threadNum)
    pool.map(sub_crawler, website_list)
    pool.close()
    pool.join()


if __name__ == "__main__":
    page_num = 1
    threadNum = 8
    # url要事先把选项选好，还有页数记好
    url1 = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index='

    url2 = '&bidSort=0&buyerName=&projectId=&pinMu=++0&bidType=1&dbselect=bidx&kw=系统&start_time=2020%3A04%3A27&end_time=2020%3A05%3A27&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='

    for num in range(1, 6):
        index = url1 + str(num) + url2
        crawler(index, threadNum)
