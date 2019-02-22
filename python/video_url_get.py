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

    def _clean_old_data(self):
        # 清理数据库中过旧数据
        HOW_LONG_IS_OLD = 14  # 多久才算旧数据？单位：天
        LONG_LONG_AGO = '1970-01-01'
        today = datetime.date.today()
        oldday = today - datetime.timedelta(days=HOW_LONG_IS_OLD)
        Log.i('清除' + str(oldday) + '之前的视频数据中....')
        sql = "delete from video_list where date(date) between '" + LONG_LONG_AGO + "' and '" + str(oldday) + "';"
        self.db.execute(sql)
        Log.i('清除完毕.')
        return True

    def _data_to_db(self, data):
        # 将data数据录入数据库,判为重则return false否则return true
        # data:json<time, title, url>
        if len(data) < 3:
            return False
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
        self._url['beijing'] = 'https://bj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=9c341beabdfaf2f02572b58f7ae946094d154578e57596ad7037393a108c652d1840e18db53d6217852592f811486071&page=1'
        self._json_url['beijing'] = 'https://bj.xuexi.cn/local/bj/channel/c8e030ce-fa58-4db0-8c92-8440498f835c.json'
        self._url['chongqing_bayu'] = 'https://cq.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=674998f7f82e1483979eb0ada48ffe2466e00c610ec179b5b982eef96009f47a02ce8d9c8c0895ffa9a4af3524a238a0&page=1'
        self._json_url['chongqing_bayu'] = 'https://cq.xuexi.cn/local/cq/channel/91a0eb52-6c45-4f05-a05e-a2a06d9d1804.json'
        self._url['chongqing_gushi'] = 'https://cq.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=f1e8b4c2d19f06e9347078cd6e076051b3c5089254f990af23681978ecf61528bf98da42bdceaa231dbd265f7b193803&page=1'
        self._json_url['chongqing_gushi'] = 'https://cq.xuexi.cn/local/cq/channel/210760a2-2f76-422e-bd2b-88922a34e580.json'
        self._url['chongqing_jiceng'] = 'https://cq.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=649a5c06437c2d0ffff43114701efa3624ccf4c1ebd755758665cc5641a58316ef8712600d5d473b047422a15d55bbca&page=1'
        self._json_url['chongqing_jiceng'] = 'https://cq.xuexi.cn/local/cq/channel/1f674f55-8dde-405e-9009-1d1a1647b957.json'
        self._url['hubei_renwu'] = 'https://hb.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=869cd6b8fdfcf82618fb1a2b07b730446227a59b7203e72f28754cc6d7fc8d439c8fc9030919ecb2e3b6b6ef173a907e&page=1'
        self._json_url['hubei_renwu'] = 'https://hb.xuexi.cn/local/hb/channel/9554dcaa-eb2c-491f-981b-3a422ba0c662.json'
        self._url['hubei_tuijian'] = 'https://hb.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=f0f7e0dc8adc7367c9f7bcc7d1ec90230f4fd2b0c5b9dd59e2eee1d65a6f98944022343c57c029a288ea1802719b632f&page=1'
        self._json_url['hubei_tuijian'] = 'https://hb.xuexi.cn/local/hb/channel/393ba1c2-204e-442c-8a11-8bc7b7611c2b.json'
        self._url['hubei_wenhua'] = 'https://hb.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=24ee8d6c42986288ed2e3faab1e791d9f7cdd2a78bc2957d43414763ba41f35578203108b5374dda2b7abf2d24ae8d10&page=1'
        self._json_url['hubei_wenhua'] = 'https://hb.xuexi.cn/local/hb/channel/b3f5e6fc-5ca9-4570-820c-edc053776eda.json'
        self._url['jiangxi'] = 'https://jx.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=8d37b02c7a99ded0394139c8601119208e5f0fa26387c261f9228ccd9daa99e607093b7885493ec9e7bbc970abdc5ef3&page=1'
        self._json_url['jiangxi'] = 'https://jx.xuexi.cn/local/jx/channel/3b61979a-4561-4347-afe4-5b9287bf8cf5.json'
        self._url['ningxia'] = 'https://nx.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=55276770940d78c9617aea967e1efded76c82e4e5a182f6bd8758872aaacb84c0da1ad224e5e157bfb8feeced36438de&page=1'
        self._json_url['ningxia'] = 'https://nx.xuexi.cn/local/nx/channel/04fb7b0d-ec10-428d-a65a-18396e35f07f.json'
        self._url['shandong_qilu'] = 'https://sd.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=430e30c2633c821be125767aa55999b2a3a7b03bb72c212149a533f6a95a6593fd5b05bbd0ee7f94c96b753e046e25d8&page=1'
        self._json_url['shandong_qilu'] = 'https://sd.xuexi.cn/local/sd/channel/f1278f22-2c51-43ac-82fe-2891ca92ddb5.json'
        self._url['shandong_story'] = 'https://sd.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=a47dd6f30405b9092e6e6804f41a3deb63cec3a6c02c70d095844d78deacaf3f3ced86f5ddc8c16e771f0c2d8c6a28ce&page=1'
        self._json_url['shandong_story'] = 'https://sd.xuexi.cn/local/sd/channel/5d7bf5de-5c0b-4872-bcdd-c0067ccecac2.json'
        self._url['shandong_xuanjiang'] = 'https://sd.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=4dd1e46b21ab3f9716399b608a4e6e5e85be983a042c1841dc0dd554ec3022d8c6304e11e3b6f2430ac4188123c4d480&page=1'
        self._json_url['shandong_xuanjiang'] = 'https://sd.xuexi.cn/local/sd/channel/05fc5b04-4376-49c4-b3a0-b506777f8757.json'
        self._url['shanxi'] = 'https://sx.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=be3f0ff12434633c64f9ae75357b2adf272eb88426f6fd8e662ba68d11acecf6743228141bff2d9baa7e27a536a935bf&page=1'
        self._json_url['shanxi'] = 'https://sx.xuexi.cn/local/sx/channel/78cbf072-8502-4423-a8e4-03324a153934.json'
        self._url['tianjin'] = 'https://tj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1716773628d5787e6652ac44576ccd8b887d24e273ff5790b9512f9ec0dd412001601b6b03409ef4b87131fa60e13802&page=1'
        self._json_url['tianjin'] = 'https://tj.xuexi.cn/local/tj/channel/0bfd33a4-c6d4-47b0-96eb-1ec3064eb21b.json'
        self._url['zhejiang'] = 'https://zj.xuexi.cn/local/list.html?6b4b63f24adaa434bb66a1ac37e849e0=1ee1d4b83e51a09bc14ea52aed4de9612bbd19ba340253f5c87cb69af1821f124f4208345a74650885428ffeffaac9ba&page=1'
        self._json_url['zhejiang'] = 'https://zj.xuexi.cn/local/zj/channel/7468c909-5672-4e76-b998-78b8d2c130f6.json'

    def start(self):
        # 开始获取视频站视频链接
        while True:
            # 先清理老数据
            self._clean_old_data()
            # 然后获取数据并录入数据库
            self.web.browser_chrome_init()
            self._get_details()
            self.web.browser_quit()
            # 最后睡觉
            Log.i('休眠中....')
            time.sleep(6 * 60 * 60)

if __name__ == '__main__':
    d = VideoUrlGet()
    d.start()
