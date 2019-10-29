import scrapy
from pixiv_spilder.items import PixivIllustItem
from pixiv_spilder.database import db

import json
import html
import datetime

class IllustSpider(scrapy.Spider):
    name = 'illust'
    dbCursor = db.cursor()

    def start_requests(self):
        illust_ids = []
        with open('illust_id.json', 'r') as f:
            illust_ids = json.load(f)
        pass
        for illust_id in illust_ids:
            self.dbCursor.execute("SELECT * FROM illust WHERE id = " + str(illust_id))
            if not self.dbCursor.fetchall():
                referer = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(illust_id)
                headers = {'referer': referer, 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
                # artRefer = 'https://www.pixiv.net/ranking.php?mode='+ mode +'&content='+ content +'&p=' + str(page)
                url = 'https://www.pixiv.net/touch/ajax/illust/details?illust_id=' + str(illust_id)
                yield scrapy.Request(url = url, headers = headers, callback = self.parseIllust)
            pass
        pass
        db.close()
    pass

    def parseIllust(self, response):
        resJson = json.loads(response.body.decode('utf-8'))
        illust_details = resJson['body']['illust_details']

        illust_item = PixivIllustItem()
        illust_item['id'] = str(illust_details.get('id'))
        illust_item['user_id'] = str(illust_details.get('user_id'))
        illust_item['title'] = illust_details.get('title')  or ''
        illust_item['upload_timestamp'] = illust_details.get('upload_timestamp') or ''
        illust_item['comment'] = html.escape(illust_details.get('comment') or '')
        illust_item['comment_html'] = html.escape(illust_details.get('comment_html') or '')
        illust_item['bookmark_user_total'] = illust_details.get('bookmark_user_total') or ''
        illust_item['rating_count'] = illust_details.get('rating_count') or ''
        illust_item['rating_view'] = illust_details.get('rating_view') or ''
        illust_item['x_restrict'] = illust_details.get('x_restrict') or ''
        illust_item['type'] = illust_details.get('type') or ''
        illust_item['created'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        tags = []
        for item in illust_details.get('display_tags') or []:
            if 'translation' in item and self.isChTag(str(item.get('translation'))):
                tags.append(item.get('translation'))
            else:
                tags.append(item.get('tag'))
            pass
        pass
		# 标签去重
        tags = list(set(tags))
        if len(tags) > 0:
            illust_item['tags'] = ',' + ','.join(tags) + ','
        else:
            illust_item['tags'] = ',插画,'
        pass

        imgs = []
        if 'manga_a' in illust_details:
            for index in range(len(illust_details['manga_a'])):
                item = illust_details['manga_a'][index]
                otherItem = illust_details['illust_images'][index]
                imgs.append({
                    'page': index,
                    'url_big': item['url_big'],
                    'width': otherItem['illust_image_width'],
                    'height': otherItem['illust_image_height'],
                })
            pass
        else:
            imgs.append({
                'page': 0,
                'url_big': illust_details['url_big'],
                'width': illust_details['width'],
                'height': illust_details['height'],
            })
        pass
        imgs = imgs[0:3]

        illust_item['imgs'] = imgs

        yield illust_item
    pass

    # 判断是否全为中文
    def isChTag(self, s):
        for ch in s:
            if '\u4e00' <= ch <= '\u9fa5':
                return True
            pass
        pass
        return False
    pass
pass
