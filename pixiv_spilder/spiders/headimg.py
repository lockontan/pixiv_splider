import scrapy
from pixiv_spilder.items import PixivImgItem
from pixiv_spilder.database import db
from pixiv_spilder.utils import getUserAget
from pixiv_spilder.settings import DOWNLOAD_IMG

import json
import datetime
import os

class IllustSpider(scrapy.Spider):
    name = 'headimg'
    dbCursor = db.cursor()

    def start_requests(self):
        headimgs = []
        with open('headimgs.json', 'r') as f:
            headimgs = json.load(f)
        pass
        for item in headimgs:
            ext = os.path.splitext(item['url'])[1]
            headers = {'referer': 'https://www.pixiv.net/member.php?id=' + str(item['user_id'])}
            yield scrapy.Request(item['url'], meta = {'user_id': item['user_id'], 'ext': ext}, headers = headers, callback = self.parseImg)
        pass
        db.close()
        print('头像获取完毕')
    pass

    def parseImg(self, response):
        filePath = os.path.join(DOWNLOAD_IMG['head_path'])
        if os.path.exists(filePath) == False :
            os.makedirs(filePath)
        pass

        fullPath = os.path.join(filePath, response.meta['user_id'] + '_head' + response.meta['ext'])

        fp = open(fullPath, 'wb')
        fp.write(response.body)
    pass
pass
