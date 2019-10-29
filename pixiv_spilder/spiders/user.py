import scrapy
from pixiv_spilder.items import PixivUserItem
from pixiv_spilder.database import db

import json
import html
import datetime
import os

class IllustSpider(scrapy.Spider):
    name = 'user'
    dbCursor = db.cursor()

    def start_requests(self):
        user_ids = []
        with open('user_id.json', 'r') as f:
            user_ids = json.load(f)
        pass
        for user_id in user_ids:
            self.dbCursor.execute("SELECT * FROM user WHERE id = " + str(user_id))
            if not self.dbCursor.fetchall():
                url = 'https://www.pixiv.net/touch/ajax/user/details?id=' + str(user_id)
                headers = {'referer': url, 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
                yield scrapy.Request(url = url, headers = headers, callback = self.parseUser)
            pass
        pass
        db.close()
    pass

    def parseUser(self, response):
        resJson = json.loads(response.body.decode('utf-8'))
        user_details = resJson.get('user_details') or resJson.get('body').get('user_details')

        user_item = PixivUserItem()
        user_item['id'] = str(user_details.get('user_id'))
        user_item['user_create_time'] = user_details.get('user_create_time') or ''
        user_item['user_name'] = user_details.get('user_name') or ''
        user_item['user_comment'] = html.escape(user_details.get('user_comment')) or '' 
        user_item['user_comment_html'] = html.escape(user_details.get('user_comment_html')) or ''
        user_item['follows'] = user_details.get('follows') or '0'
        user_item['user_account'] = user_details.get('user_account') or '0'
        user_item['user_sex'] = user_details.get('user_sex') or '3'
        user_item['location'] = user_details.get('location') or ''
        user_item['user_country'] = user_details.get('user_country') or ''

        if user_details['cover_image']:
            user_item['cover_image'] = 'https://i.pximg.net/c/background/img' + user_details['cover_image']['profile_cover_filename'] + '.' + user_details['cover_image']['profile_cover_ext']
        else:
            user_item['cover_image'] = ''
        pass

        if user_details.get('profile_img'):
            user_item['profile_img_origin'] = user_details['profile_img']['main']
            user_item['profile_img_main'] = '/pixiv/headimg/' + user_item['id'] + '_head' + os.path.splitext(user_details['profile_img']['main'])[1]
            user_item['profile_img_main_s'] = user_details['profile_img']['main_s']
        else:
            user_item['profile_img_origin'] = ''
            user_item['profile_img_main'] = ''
            user_item['profile_img_main_s'] = ''
        pass

        if user_details.get('social'):
            keys = user_details['social'].keys()
            if 'pawoo' in keys:
                user_item['social_pawoo_url'] = user_details['social']['pawoo']['url']
            else:
                user_item['social_pawoo_url'] = ''
            pass
            if 'twitter' in keys:
                user_item['social_twitter_url'] = user_details['social']['twitter']['url']
            else:
                user_item['social_twitter_url'] = ''
            pass
        else:
            user_item['social_pawoo_url'] = ''
            user_item['social_twitter_url'] = ''
        pass
        yield user_item
    pass
pass
