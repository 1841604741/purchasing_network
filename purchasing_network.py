import requests
from bs4 import BeautifulSoup
import json
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

def frame(url):
    '''
    用于切换页面iframe
    :param url:
    :return:返回最新页面的HTML
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--window-size=1920, 1080")

    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("disable-infobars")

    # chrome_options.add_argument()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # 禁止加载
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            # 'javascript': 2,
            'permissions.default.stylesheet': 2
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    iframe = driver.find_element_by_xpath('//*[@id="detail_frame"]')
    driver.switch_to.frame(iframe)
    return driver.page_source
# 贵州数据爬取还有问题
def guizhou(location):
    for i in range(1,3):
        data = {
                "categoryCode": "ZcyAnnouncement6",
                "districtCode":
                [
                    "520",
                    "522"
                ],
                "pageNo": i,
                "pageSize": 15,
                "utm": "sites_group_front.2ef5001f.0.0.77b3a170cad111ed965a318cc28b7f3a",
        }
        head = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Cookie": "_zcy_log_client_uuid=77b1a5a0-cad1-11ed-965a-318cc28b7f3a",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "http://www.ccgp-guizhou.gov.cn/ZcyAnnouncement/ZcyAnnouncement6/index.html?districtCode=520,522&utm=sites_group_front.2ef5001f.0.0.77b3a170cad111ed965a318cc28b7f3a"

        }
        # http://www.ccgp-guizhou.gov.cn/ZcyAnnouncement/ZcyAnnouncement6/index.html?districtCode=520,522&utm=sites_group_front.2ef5001f.0.0.77b3a170cad111ed965a318cc28b7f3a
        url = r'http://www.ccgp-guizhou.gov.cn/ZcyAnnouncement/ZcyAnnouncement6/index.html'
        resp = requests.post(url,headers=head,data=data)
        print(resp,resp.text)

def zhejiang(location):
    for i in range(1,2):  #目前总共有666页
        url = r'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        param = {
            "pageSize": 15,
            "pageNo": i,
            "sourceAnnouncementType": "10016,3012,1002,1003,3014,3013,3009,4004,3008,2001,3001,3020,3003,3002,3011,3017,3018,3005,3006,3004,"
                                      "4005,4006,3007,3015,3010,3016,6003,4002,4001,4003,8006,1995,1996,1997,8008,8009,8013,8014,9002,9003,808030100,"
                                      "7003,7004,7005,7006,7007,7008,7009",
            "isGov": "true",
            "url": "notice",
        }
        resp = (requests.get(url,headers=headers,params=param)).json()
        for articles in resp['articles']:
            title_id = articles['id']
            title_name = articles['title']
            title_href = articles['url']
            # print(title_id,title_name,title_href)

            title_resp = frame(title_href)
            try:
                title_soup = BeautifulSoup(title_resp,'html.parser')
                for ul in title_soup.select('.fjxx>li'):
                    fujian_href = ul.select(' p>a')[0].get('href')
                    title_format = (ul.select(' p>a')[0].text).split('.')[-1]
                    print(fujian_href,title_id,title_name)
                    # 判断是否存在这个文件夹
                    if not os.path.exists(os.path.join(f'./{location}')):
                        os.makedirs(f'./{location}')
                        # 判断这个附件是否存在
                    if not os.path.exists(os.path.join(f'./{location}/{title_id}.{title_format}')):
                        with open(f'./{location}/{title_id}.{title_format}',mode='wb',) as f:
                            f.write((requests.get(fujian_href)).content)
            except Exception as e:
                print(e)

def henan(location):
    channelCode = ['9102','1401','1402','1301','9101','1304']
    # channelCode = ['9102','1401']
    for code in channelCode:
        url = r'http://pingdingshan.hngp.gov.cn/pingdingshan/list2'
        param1 = {
            "channelCode": code,
            "pageNo": 1,
            "pageSize": 16,
            "bz": 1,
            "gglx": 0
        }
        resp1 = requests.get(url,params=param1)
        soup1 = BeautifulSoup(resp1.text,'html.parser')
        pageInfo = (soup1.select('.pageInfo')[0].text.strip()).replace('共 ','').replace(' 页','')
        for bz in range(1,3):
            for pageNo in range(1,int(pageInfo)):
                param = {
                    "channelCode": code,
                    "pageNo": pageNo,
                    "pageSize": 16,
                    "bz": bz,
                    "gglx": 0
                }
                resp = requests.get(url, params=param)
                soup = BeautifulSoup(resp.text, 'html.parser')
                for row in soup.select('.List2>ul>li'):
                    title = row.select('a')[0].text
                    title_href = 'http://pingdingshan.hngp.gov.cn' + row.select('a')[0].get('href')
                    title_resp = requests.get(title_href)
                    resp_soup = BeautifulSoup(title_resp.text, 'html.parser')
                    try:
                        for file in resp_soup.select('div.List1.Top5>ul>li'):
                            file_href = 'http://pingdingshan.hngp.gov.cn' + file.select('a')[0].get('href')
                            file_href_name = file_href.split('/')[-1].split('.')[0]  #获取文件名字
                            file_format = (file.select('a')[0].text).split('.')[-1]  #获取文件格式
                            print(title,file_href_name)
                            # 判断是否存在这个文件夹
                            if not os.path.exists(os.path.join(f'./{location}')):
                                os.makedirs(f'./{location}')
                                # 判断这个附件是否存在
                            if not os.path.exists(os.path.join(f'./{location}/{file_href_name}.{file_format}')):
                                with open(f'./{location}/{file_href_name}.{file_format}', mode='wb', ) as f:
                                    f.write((requests.get(file_href)).content)
                    except Exception as e:
                        print(e)

def shaanxi(location):
    try:
        sxTree_data = json.load(open('./sxTree.json',mode='r',encoding='utf-8'))
    except:
        sxTree_data = json.load(open('./sxTree.json', mode='r', encoding='gbk'))
    regionCode_list = []
    regionCode_list.append(610001)
    for code1 in sxTree_data:
        if '全部' in  code1['name'] or '省本级' in  code1['name']:continue
        for code2 in code1['children']:
            regionCode_list.append(code2['regionCode'])
    noticeType = ['00101,001011','001021,001022,001023,001024,001025,001026,001029,001006','001031,001032','001004,001006','001053,001052,00105B',
                  '001051,00105F','59,5E','001054,00100B','00105A,001009,00100C','001062']
    for code in regionCode_list:
        time.sleep(0.5)
        for type in noticeType:
            time.sleep(0.5)
            for i in range(1,20):
                time.sleep(0.5)
                url = r'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do'
                param = {
                    "siteId": "a7a15d60-de5b-42f2-b35a-7e3efc34e54f",
                    "channel": "1eb454a2-7ff7-4a3b-b12c-12acc2685bd1",
                    "currPage": i,
                    "pageSize": 10,
                    "noticeType": type,
                    "regionCode": code,
                    "purchaseManner": "",
                    "title":"" ,
                    "openTenderCode":'' ,
                    "purchaseNature": "",
                    "operationStartTime": "",
                    "operationEndTime": "",
                    "selectTimeName": "noticeTime",
                    "cityOrArea": "",
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                }
                resp = (requests.get(url,params=param,headers=headers)).json()
                for pageurl in resp['data']:
                    pageurl1 = 'http://www.ccgp-shaanxi.gov.cn'+pageurl['pageurl']
                    shorttitle = pageurl['shorttitle']
                    resp_title = requests.get(pageurl1,headers=headers)
                    soup = BeautifulSoup(resp_title.text,'html.parser')
                    try:
                        for file in soup.select('#content > div > div:nth-child(2) > div'):
                            file_href = file.select('a')[0].get('href')
                            file_format = (file.select('a')[0].text).split('.')[-1]
                            file_href_name = file_href.split('/')[-1].split('=')[-1]
                            print(shorttitle,file_href_name)
                            # 判断是否存在这个文件夹
                            if not os.path.exists(os.path.join(f'./{location}')):
                                os.makedirs(f'./{location}')
                                # 判断这个附件是否存在
                            if not os.path.exists(os.path.join(f'./{location}/{file_href_name}.{file_format}')):
                                with open(f'./{location}/{file_href_name}.{file_format}', mode='wb', ) as f:
                                    f.write((requests.get(file_href)).content)
                    except Exception as e:
                        print(e)

def hainan(location):
    # 首先获取总共的页面数
    url_page = r'https://www.ccgp-hainan.gov.cn/cgw/cgw_list_cgxx.jsp?currentPage=1'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    resp_page = requests.get(url_page,headers=headers)
    soup_page = BeautifulSoup(resp_page.text,'html.parser')
    page_sum = (soup_page.select('body > div.cg20-zt > div.cg20-gl > div > div.nei02_04_02 > form > ul > li > a:nth-child(2)')[0].get('href')).split('=')[-1]

    for page in range(1,int(page_sum)):
        url = f'https://www.ccgp-hainan.gov.cn/cgw/cgw_list_cgxx.jsp?currentPage={page}'
        resp = requests.get(url,headers=headers)
        soup = BeautifulSoup(resp.text,'html.parser')
        for row in soup.select('.nei03_04_08>ul>li'):
            type = row.select('span>tt>a')[0].text  # 采购类型
            sourcing_places = row.select('span>b>a')[0].text# 采购地方
            title = row.select('em>a')[0].text  #采购标题
            title_href = 'https://www.ccgp-hainan.gov.cn' +row.select('em>a')[0].get('href')  #采购详情链接
            company = row.select('h5>a')[0].text # 采购公司
            print(company,title_href)

            resp_title = requests.get(title_href,headers=headers)
            try:
                soup_title = BeautifulSoup(resp_title.text,'html.parser')
                for file in soup_title.select('.content03'):
                    file_href = file.select('a')[1].get('href')
                    file_href_name = file_href.split('/')[0].split('.')[0]
                    file_format = file_href.split('.')[-1]
                    print(file_href,file_href_name)
            except:
                pass

if __name__ == '__main__':

    location = input('请输入采集的地方：')
    if location == '贵州':
        guizhou(location)
    elif location == '浙江':
        zhejiang(location)
    elif location == '河南':
        henan(location)
    elif location == '陕西':
        shaanxi(location)
    elif location == '海南':
        hainan(location)