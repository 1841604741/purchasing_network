import requests
import os
import urllib.request as urllib2
from selenium import webdriver
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image


if __name__ == '__main__':
    url = r'https://zfcg.czt.fujian.gov.cn/freecms/site/fujian/xmgg/index.html'
    driver = webdriver.Chrome(r"D:\Egg_Project\chromedriver.exe")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    verification_img =   'https://zfcg.czt.fujian.gov.cn/' + soup.select('#code_img')[0].get('src')
    print(verification_img)
    verification_img_name = os.path.basename(verification_img).split('&')[-1]
    with open(f'./验证码图片/{verification_img_name}.jfif',mode='wb') as f:
        f.write(requests.get(verification_img).content)

    # 获取验证码的数字
    verification_img_text = pytesseract.image_to_string(Image.open(f'./验证码图片/{verification_img_name}.jfif'), lang="eng")
    print(verification_img_text)
    driver.find_element_by_css_selector('#verifycode').click()
    driver.find_element_by_css_selector('#verifycode').clear()
    driver.implicitly_wait(10)
    driver.find_element_by_css_selector('#Inquire').click()
    url_json = r'https://zfcg.czt.fujian.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do'
    for i in range(1,16433):
        param = {
            "siteId": "d36a6e8b-4363-4b52-a00b-79ca47033923",
            "channel": "f582600e-065d-4f35-8966-48a33fa93863",
            "currPage": i,
            "pageSize": 10,
            "noticeType": '',
            "regionCode": 350001,
            "purchaseManner":'' ,
            "title": '',
            "verifyCode": 3898,
            "openTenderCode": '',
            'purchaser': '',
            "agency": '',
            "purchaseNature": '',
            "operationStartTime": '',
            "operationEndTime": '',
            "selectTimeName": "noticeTime",
            "cityOrArea": "",
        }
        resp_json = (requests.get(url_json,params=param)).json()
        for pageurl  in resp_json['data']:
            pageurls = pageurl['pageurl']
            resp_pageurl = requests.get(pageurls)
            pageurl_soup = BeautifulSoup(resp_pageurl.text,'html.parser')
            try:
                file_url = pageurl_soup.select('')
            except:pass

    driver.close()

