import datetime
import json
import requests
import time
from log import Log
from selenium import webdriver
from settings import *

# chrome版本与webdriver对应表
# https://blog.csdn.net/huilan_same/article/details/51896672
# apis
# https://blog.csdn.net/u010986776/article/details/79266448#

class WebControl(object):
    # 浏览器控制类

    def __init__(self):
        pass

    def browser_chrome_init(self):
        # chrome配置
        Log.i('Chrome浏览器创建中....')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        options._binary_location = CHROME_LOCATION
        self.driver = webdriver.Chrome(chrome_options=options)

    def get_delt_date_before_today(self, timestr):
        # 获取日期在今天的前面几天
        # timestr:'%Y-%m-%d %H:%M:%S'
        # return:日数差,不考虑时间
        now_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date = datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')  #按格式转换
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)  #这里的date是变量
        return (now_time - date).days

    def get_detail_json_by_title(self, item):
        # 在当前页面根据title打开页面并获取页面url/insertTime/title然后关闭
        # return:页面detail json
        title = item['itemTitle']
        title = ''.join(title.split())
        elements = self.driver.find_elements_by_tag_name('a')
        #Log.d('当前title:' + title[0:18])
        for i in elements:  #判断每个a元素内部内容是否与title相同
            #Log.d('当前元素内容：' + ''.join(i.get_attribute('text').split()))
            if ''.join(i.get_attribute('text').split())[0:18] == title[0:18]:  # 长度超过20多就会变点点点,因此只比对前19位
                i.click()
                break
        # 如果没有点击到是不能继续执行的
        if len(self.driver.window_handles) == 1:
            return {}
        self.driver.switch_to_window(self.driver.window_handles[-1])  #切到新打开的页面
        self.wait_for_loading()
        cur_url = self.driver.current_url
        Log.i('获取到标题为' + item['itemTitle'] + '的视频页面url: ' + cur_url)
        self.driver.close()  #关闭页面
        self.wait_for_loading()
        self.driver.switch_to_window(self.driver.window_handles[0])  #切回页面
        ret = {
            'time': item['insertTime'],
            'title': item['itemTitle'],
            'url': cur_url,
        }
        return ret

    def get_json(self, url):
        # 获取json数据并返回
        # url:链接
        # return:json data
        response = requests.get(url)
        res = json.loads(response.text)
        return res

    def go(self, url):
        return self.driver.get(url)

    def is_time_valid(self, json_item_time):
        # 判断文章视频json_item项的时间是否合法(仅搜索昨天和今天的新闻,昨天的给明天用户用)
        delt_time = self.get_delt_date_before_today(json_item_time)
        if delt_time == 0 or delt_time == 1:
            return True
        return False

    def wait_for_loading(self):
        time.sleep(1)

if __name__ == "__main__":
    t = WebControl()
    t.browser_chrome_init()
