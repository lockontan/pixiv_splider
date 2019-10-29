import scrapy
from pixiv_spilder.items import PixivImgItem
from pixiv_spilder.database import db
from pixiv_spilder.utils import getUserAget, getBeforeDate
from pixiv_spilder.settings import DOWNLOAD_IMG, UPDATE_INI_PATH

import json
import datetime
import os
import configparser
import requests

class IllustSpider(scrapy.Spider):
    name = 'img'
    dbCursor = db.cursor()

    def start_requests(self):
        illusts = []
        with open('imgs.json', 'r') as f:
            illusts = json.load(f)
        pass
        for illust in illusts:
            headers = {
                'referer': 'https://www.pixiv.net/member_illust.php?mode=big&illust_id=' + str(illust['id']),
                'user-agent': getUserAget()
            }
            for item in illust['imgs']:
                fileExt = os.path.splitext(item['url_big'])[1]
                rename = str(illust['id']) + '_p' + str(item['page']) + fileExt
                yield scrapy.Request(item['url_big'], headers = headers, meta = {'rename': rename, 'id': str(illust['id']), 'page': item['page']}, callback = self.parseImg)
            pass
        pass
        db.close()

        # 更新排行最新日期
        # conf = configparser.ConfigParser()
        # conf.add_section('date')
        # conf.set('date', 'update', getBeforeDate(1))
        # with open(UPDATE_INI_PATH, 'r+') as conffile:
        #     conf.write(conffile)
        # pass
        
        r = requests.post('https://tanzijun.com/api/ranking/update', params = {'date': getBeforeDate(1)})
        print(r.text)
    pass

    def parseImg(self, response):
        filePath = os.path.join(DOWNLOAD_IMG['path'], response.meta['id'])
        if os.path.exists(filePath) == False :
            os.makedirs(filePath)
        pass

        fullPath = os.path.join(filePath, response.meta['rename'])

        fp = open(fullPath, 'wb')
        fp.write(response.body)

        img_item = PixivImgItem()
        img_item['path'] = fullPath
        img_item['page'] = response.meta['page']
        img_item['id'] = response.meta['id']
        yield img_item
    pass
pass
