import json
import requests
import time
import urllib3
from selenium import webdriver

# chrome版本与webdriver对应表
# https://blog.csdn.net/huilan_same/article/details/51896672
# apis
# https://blog.csdn.net/u010986776/article/details/79266448#

class Main(object):
    _url = dict()
    _json = dict()
    def __init__(self):
        self.local_url_define()
        self.browser_chrome_init()

    def browser_chrome_init(self):
        # chrome配置
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        options._binary_location = 'F:\\Browser\\Google\\Chrome\\Application\\chrome.exe'
        self.driver = webdriver.Chrome(chrome_options=options)

    def display_website(self, place):
        # 在浏览器中显示站点
        self.driver.get(self._url[place])
        self.wait_for_loading()

    def get_vdo_json(self, place):
        # 获取视频集json数据并返回
        # place:str,地方拼音
        # return:vdo json data
        timestamp = int(time.time() * 10)
        response = requests.get(self._json[place])
        res = json.loads(response.text)
        return res

    def local_url_define(self):
        # 定义地方视频集地址和json数据获取地址
        self._url['zhejiang'] = 'https://zj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1ee1d4b83e51a09bc14ea52aed4de9612bbd19ba340253f5c87cb69af1821f124f4208345a74650885428ffeffaac9ba&page=1'
        self._json['zhejiang'] = 'https://zj.xuexi.cn/local/zj/channel/7468c909-5672-4e76-b998-78b8d2c130f6.json'

    def open_by_title(self, title):
        # 在当前页面根据title打开页面
        # return:页面url
        title = ''.join(title.split())
        elements = self.driver.find_elements_by_tag_name('a')
        for i in elements:
            if(''.join(i.get_attribute('text').split()) == title):
                i.click()
                break
        self.wait_for_loading()
        return self.driver.current_url

    def wait_for_loading(self):
        time.sleep(2)

if __name__ == "__main__":
    t = Main()
    t.display_website('zhejiang')
    json = t.get_vdo_json('zhejiang')
    t.open_by_title(json['items'][0]['itemTitle'])
    #t.test()
