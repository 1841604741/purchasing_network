import requests

from bs4 import BeautifulSoup
from selenium import webdriver
# http://www.ccgp.gov.cn/oss/download?uuid=5905e924-186f85bab03-4f44feecf
from webdriver_manager.chrome import ChromeDriverManager

for i in range(1,26):   #总共页数：120441
    url = f'http://htgs.ccgp.gov.cn/GS8/contractpublish/index_{i}'
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
    # driver = webdriver.Chrome(executable_path=r"D:\chromedriver.exe", options=chrome_options)

    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    resp = requests.get(url,headers=head)
    soup = BeautifulSoup(resp.text,'html.parser')
    for raw in soup.select('.ulst>li')[1:]:  #跳过第一“li”
        title = raw.select('a')[0].get('title')  #项目名称
        title_href = 'http://htgs.ccgp.gov.cn/GS8/contractpublish'+(raw.select('a')[0].get('href'))[1:]  #项目链接
        signing_time = raw.select('div>span')[0].text.strip()  # 签订时间
        release_time = raw.select('span')[1].text.strip()   # 发布时间
        purchaser = raw.select('span')[2].text.strip()    # 采购人
        vendor = raw.select('span')[3].text.strip()     #  供应商
        print(title,title_href,signing_time,release_time,purchaser,vendor)
        try:
            driver.get(title_href)
            driver.find_element_by_id().click()
            # 获取资源链接
            resource_link = driver.current_url
            # 关闭浏览器
            driver.quit()
        except:pass


