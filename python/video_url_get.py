import datetime
import time
from log import Log
from database_control import DBControl
from web_control import WebControl

class VideoUrlGet(object):
    # 控制浏览器进行地方视频站视频获取
    _url = dict()  #存放地方视频站
    _json_url = dict()  #存放地方视频站内容分发json

    def __init__(self):
        # 初始化时需新建浏览器控制器
        self._local_url_define()  #初始化url表
        self.db = DBControl()  #初始化数据库控制器
        self.web = WebControl()  #初始化浏览器控制器
        self.web.browser_chrome_init()

    def _display_local_vdo_website(self, place):
        # 在浏览器中显示地方视频站点
        Log.i('加载' + place + '地方视频站页面中....')
        self.web.go(self._url[place])
        self.wait_for_loading()

    def _get_details(self):
        # 获取每个地方视频站视频的包含url在内的详情
        # return: json[]
        results = []
        for key in self._url.keys():
            # 获取json分发,并打开网站
            json = self._get_vdo_json(key)
            self._display_local_vdo_website(key)
            # 遍历网站标题获取url直到日期过旧
            for item in json['items']:
                if self.web.is_time_valid(item['insertTime']):  #日期新
                    results.append(self.web.get_detail_json_by_title(item))
                else:  #日期过旧
                    break
        return results

    def _get_vdo_json(self, place):
        # 获取视频集json数据并返回
        # place:str,地方拼音
        # return:vdo json data
        Log.i('获取' + place + '视频站视频列表内容json中....')
        timestamp = int(time.time() * 10)
        json = self.web.get_json(self._json_url[place] + '?' + str(timestamp))
        return json

    def have_enough_url_yesterday(self):
        # 查库判断是否有足够的昨日视频链接库存
        ITEM_LIMIT = 20  #限制视频链接封顶库存数量
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        res = self.db.search('select count(url) from video_list where date=\'' + str(today) + '\'')
        Log.i('昨日(' + str(today) + ')视频链接库存: ' + str(res[0][0]))
        if res[0][0] >= ITEM_LIMIT:
            return True
        return False

    def _local_url_define(self):
        # 定义地方视频集地址和json数据获取地址
        self._url['zhejiang'] = 'https://zj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1ee1d4b83e51a09bc14ea52aed4de9612bbd19ba340253f5c87cb69af1821f124f4208345a74650885428ffeffaac9ba&page=1'
        self._json_url['zhejiang'] = 'https://zj.xuexi.cn/local/zj/channel/7468c909-5672-4e76-b998-78b8d2c130f6.json'

    def start(self):
        # 开始获取视频站视频链接
        while True:
            if not self.have_enough_url_yesterday():  #如果没有足够库存
                Log.i('没有足够库存,开始搜罗数据.')

            Log.i('休眠中....')
            time.sleep(6 * 60 * 60)

if __name__ == '__main__':
    d = VideoUrlGet()
    d.start()
