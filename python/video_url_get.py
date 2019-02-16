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

    def _data_to_db(self, data):
        # 将data数据录入数据库,判为重则return false否则return true
        # data:json<time, title, url>
        time = data['time']
        title = data['title']
        url = data['url']
        date = time.split()[0]
        # 判重
        sql = 'select count(*) from video_list where url=\'' + url + '\''
        res = self.db.search(sql)
        if res[0][0] > 0:  #有重了
            Log.i('Url已存在数据库.')
            return False
        # 才能录入
        sql = 'insert into video_list (date, title, url) values (\'' + date + '\',\'' + title + '\',\'' + url + '\')'
        self.db.execute(sql)
        return True

    def _datas_to_db(self, datas):
        # 将datas数据录入数据库,注意判重
        # datas:list<json<time, title, url>>
        Log.d('datas:' + str(datas))
        for i in datas:
            time = i['time']
            title = i['title']
            url = i['url']
            date = time.split()[0]
            # 判重
            sql = 'select count(*) from video_list where url=\'' + url + '\''
            res = self.db.search(sql)
            if res[0][0] > 0:  #有重了
                Log.i('Url已存在数据库.')
                continue
            # 才能录入
            sql = 'insert into video_list (date, title, url) values (\'' + date + '\',\'' + title + '\',\'' + url + '\')'
            self.db.execute(sql)

    def _display_local_vdo_website(self, place):
        # 在浏览器中显示地方视频站点
        Log.i('加载' + place + '地方视频站页面中....')
        self.web.go(self._url[place])
        self.web.wait_for_loading()

    def _get_details(self):
        # 获取每个地方视频站视频的包含url在内的详情并存入数据库
        # datas: list<json<time, title, url>>
        for key in self._url.keys():
            if self._have_enough_url_yesterday():
                Log.i('库存充足,继续睡觉.')
                break
            Log.i('没有足够库存,开始搜罗数据.')
            #datas = []
            # 获取json分发,并打开网站
            json = self._get_vdo_json(key)
            self._display_local_vdo_website(key)
            # 遍历网站标题获取url直到日期过旧
            for item in json['items']:
                if self.web.is_time_valid(item['insertTime']):  #日期新
                    if item['itemType'] == 30:  #是视频类型
                        #datas.append(self.web.get_detail_json_by_title(item))
                        if not self._data_to_db(self.web.get_detail_json_by_title(item)):  #判重了
                            Log.i('该页面没有检测到更新内容.')
                            break
                else:  #日期过旧
                    break
            #self._datas_to_db(datas)

    def _get_vdo_json(self, place):
        # 获取视频集json数据并返回
        # place:str,地方拼音
        # return:vdo json data
        Log.i('获取' + place + '视频站视频列表内容json中....')
        timestamp = int(time.time() * 10)
        json = self.web.get_json(self._json_url[place] + '?' + str(timestamp))
        return json

    def _have_enough_url_yesterday(self):
        # 查库判断是否有足够的昨日视频链接库存
        ITEM_LIMIT = 20  #限制视频链接封顶库存数量
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        res = self.db.search('select count(url) from video_list where date=\'' + str(yesterday) + '\'')
        Log.i('昨日(' + str(yesterday) + ')视频链接库存: ' + str(res[0][0]))
        if res[0][0] >= ITEM_LIMIT:
            return True
        return False

    def _local_url_define(self):
        # 定义地方视频集地址和json数据获取地址
        self._url['anhui'] = 'https://ah.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=9f027f78de7c86989dede5f02d283ad9a40c1585b8882a51e3ceee457d40dc2f3963303d3efaa214874d9da34cb63e64&page=1'
        self._json_url['anhui'] = 'https://ah.xuexi.cn/local/ah/channel/1bac2b93-8f63-4e4b-8378-cd14687dea0a.json'
        self._url['chongqing'] = 'https://cq.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=f1e8b4c2d19f06e9347078cd6e076051b3c5089254f990af23681978ecf61528bf98da42bdceaa231dbd265f7b193803&page=1'
        self._json_url['chongqing'] = 'https://cq.xuexi.cn/local/cq/channel/210760a2-2f76-422e-bd2b-88922a34e580.json'
        self._url['ningxia'] = 'https://nx.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=55276770940d78c9617aea967e1efded76c82e4e5a182f6bd8758872aaacb84c0da1ad224e5e157bfb8feeced36438de&page=1'
        self._json_url['ningxia'] = 'https://nx.xuexi.cn/local/nx/channel/04fb7b0d-ec10-428d-a65a-18396e35f07f.json'
        self._url['shandong'] = 'https://sd.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=430e30c2633c821be125767aa55999b2a3a7b03bb72c212149a533f6a95a6593fd5b05bbd0ee7f94c96b753e046e25d8&page=1'
        self._json_url['shandong'] = 'https://sd.xuexi.cn/local/sd/channel/f1278f22-2c51-43ac-82fe-2891ca92ddb5.json'
        self._url['shanxi'] = 'https://sx.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=be3f0ff12434633c64f9ae75357b2adf272eb88426f6fd8e662ba68d11acecf6743228141bff2d9baa7e27a536a935bf&page=1'
        self._json_url['shanxi'] = 'https://sx.xuexi.cn/local/sx/channel/78cbf072-8502-4423-a8e4-03324a153934.json'
        self._url['tianjin'] = 'https://tj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1716773628d5787e6652ac44576ccd8b887d24e273ff5790b9512f9ec0dd412001601b6b03409ef4b87131fa60e13802&page=1'
        self._json_url['tianjin'] = 'https://tj.xuexi.cn/local/tj/channel/0bfd33a4-c6d4-47b0-96eb-1ec3064eb21b.json'
        self._url['zhejiang'] = 'https://zj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1ee1d4b83e51a09bc14ea52aed4de9612bbd19ba340253f5c87cb69af1821f124f4208345a74650885428ffeffaac9ba&page=1'
        self._json_url['zhejiang'] = 'https://zj.xuexi.cn/local/zj/channel/7468c909-5672-4e76-b998-78b8d2c130f6.json'

    def start(self):
        # 开始获取视频站视频链接
        while True:
            # 获取数据并录入数据库
            self._get_details()
            # 然后清理老数据 TODO

            # 最后睡觉
            Log.i('休眠中....')
            time.sleep(6 * 60 * 60)

if __name__ == '__main__':
    d = VideoUrlGet()
    d.start()
