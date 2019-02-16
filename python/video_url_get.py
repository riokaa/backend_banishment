
from log import Log
from database_control import DBControl
from web_control import WebControl

class VideoUrlGet(object):
    # 控制浏览器进行地方视频站视频获取
    _url = dict()  #存放地方视频站
    _json_url = dict()  #存放地方视频站内容分发json

    def __init__(self):
        # 初始化时需新建浏览器控制器
        self.local_url_define()  #初始化url表
        self.db = DBControl()  #初始化数据库控制器
        self.web = WebControl()  #初始化浏览器控制器
        self.web.browser_chrome_init()

    def display_local_vdo_website(self, place):
        # 在浏览器中显示地方视频站点
        Log.i('加载' + place + '地方视频站页面中....')
        self.web.go(self._url[place])
        self.wait_for_loading()

    def get_vdo_json(self, place):
        # 获取视频集json数据并返回
        # place:str,地方拼音
        # return:vdo json data
        Log.i('获取' + place + '视频站视频列表内容json中....')
        timestamp = int(time.time() * 10)
        json = self.web.get_json(self._json_url[place] + '?' + str(timestamp))
        return json

    def local_url_define(self):
        # 定义地方视频集地址和json数据获取地址
        self._url['zhejiang'] = 'https://zj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1ee1d4b83e51a09bc14ea52aed4de9612bbd19ba340253f5c87cb69af1821f124f4208345a74650885428ffeffaac9ba&page=1'
        self._json_url['zhejiang'] = 'https://zj.xuexi.cn/local/zj/channel/7468c909-5672-4e76-b998-78b8d2c130f6.json'

    def start():
        # 开始获取视频站视频链接
        while True:


if __name__ == '__main__':
    d = VideoUrlGet()
    d.start()
