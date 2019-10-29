# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pixiv_spilder.items import PixivRankItem, PixivIllustItem, PixivImgItem, PixivUserItem
from twisted.enterprise import adbapi
from pixiv_spilder.database import db

import scrapy
import json
import os
import time
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class PixivRankPipeline(object):

    def __init__(self,dbpool):
        self.dbpool = dbpool
        self.userIds = []
        self.illustIds = []
        self.dbCursor = db.cursor()
    pass

    @classmethod
    def from_crawler(cls, crawler):
        parmas = {
            'host': crawler.settings['MYSQL_SETTINGS']['host'],
            'user': crawler.settings['MYSQL_SETTINGS']['user'],
            'password': crawler.settings['MYSQL_SETTINGS']['password'],
            'db': crawler.settings['MYSQL_SETTINGS']['db'],
            'port': crawler.settings['MYSQL_SETTINGS']['port'],
            'charset': crawler.settings['MYSQL_SETTINGS']['charset'],
        }

        dbpool = adbapi.ConnectionPool(
            'pymysql',
            **parmas
        )
        return cls(dbpool)
    pass

    def process_item(self, item, spider):
        if isinstance(item, PixivRankItem):
            self.dbCursor.execute("SELECT * FROM ranking WHERE date = '" + item['date'] + "' AND rank = " + item['rank'] + " AND mode = '" + item['mode'] + "'")
            if not self.dbCursor.fetchall():
                if item['illust_id'] not in self.illustIds:
                    self.illustIds.append(item['illust_id'])
                pass
                
                if item['user_id'] not in self.userIds:
                    self.userIds.append(item['user_id'])
                pass
                
                query = self.dbpool.runInteraction(
                    self.insert_data_todb,
                    item,
                    spider
                )
            
                query.addErrback(
                    self.handle_error,
                    item
                )
            pass
        else:
            return item
        pass
    pass

    def insert_data_todb(self,cursor,item,spider):
        sql = 'INSERT INTO ranking(mode, content, user_id, illust_id, rank, date) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (item['mode'], item['content'], item['user_id'], item['illust_id'], item['rank'], item['date']))
        print('插入成功')
    pass

    def handle_error(self,failure,item):
        print(failure)
        print('插入错误')
    pass

    def close_spider(self, spider):
        if len(self.illustIds) > 0:
            with open('illust_id.json', 'w', encoding = 'utf-8') as f:
                f.write(json.dumps(self.illustIds))
            pass
        pass
        if len(self.userIds) > 0:
            with open('user_id.json', 'w', encoding = 'utf-8') as f:
                f.write(json.dumps(self.userIds))
            pass
        pass
        self.dbpool.close()
    pass
pass

class PixivIllustPipeline(object):

    def __init__(self,dbpool):
        self.dbpool = dbpool
        self.imgs = []
    pass

    @classmethod
    def from_crawler(cls, crawler):
        parmas = {
            'host': crawler.settings['MYSQL_SETTINGS']['host'],
            'user': crawler.settings['MYSQL_SETTINGS']['user'],
            'password': crawler.settings['MYSQL_SETTINGS']['password'],
            'db': crawler.settings['MYSQL_SETTINGS']['db'],
            'port': crawler.settings['MYSQL_SETTINGS']['port'],
            'charset': crawler.settings['MYSQL_SETTINGS']['charset'],
        }

        dbpool = adbapi.ConnectionPool(
            'pymysql',
            **parmas
        )
        return cls(dbpool)
    pass

    def process_item(self, item, spider):
        if isinstance(item, PixivIllustItem):
            self.imgs.append({
                'id': item['id'],
                'imgs': item['imgs']
            })
            
            query = self.dbpool.runInteraction(
                self.insert_data_todb,
                item,
                spider
            )
        
            query.addErrback(
                self.handle_error,
                item
            )
        pass
        return item
    pass

    def insert_data_todb(self,cursor,item,spider):
        sql = 'INSERT INTO illust(id, user_id, title, upload_timestamp, comment, comment_html, bookmark_user_total, rating_count, rating_view, x_restrict, type, created, imgs, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (item['id'], item['user_id'], item['title'], item['upload_timestamp'], item['comment'], item['comment_html'], item['bookmark_user_total'], item['rating_count'], item['rating_view'], item['x_restrict'], item['type'], item['created'], json.dumps(item['imgs']), item['tags']))
        print('插入成功')
    pass

    def handle_error(self,failure,item):
        print(failure)
        print('插入错误')
    pass

    def close_spider(self, spider):
        if len(self.imgs) > 0:
            with open('imgs.json', 'w', encoding = 'utf-8') as f:
                f.write(json.dumps(self.imgs))
            pass
        pass
        self.dbpool.close()
    pass
pass

class PixivImgPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, PixivImgItem):
            fileName = item['id'] + '_p' + str(item['page'])
            pathSpilt = item['path'].split('.')
            fileExt = pathSpilt[len(pathSpilt) - 1]
            filePath = os.path.dirname(item['path'])

            img = Image.open(item['path'])
            imgWidth = img.width
            imgHeight = img.height

            # 中等图大小
            middleSize = (500, 500 / imgWidth * imgHeight)

            if str(item['page']) == '0':
                # 图片剪裁区域
                cropContent = (0, 0, imgWidth, imgHeight)
                if imgWidth > imgHeight:
                    cropContent = (0, 0, imgHeight, imgHeight)
                elif imgWidth < imgHeight:
                    cropContent = (0, 0, imgWidth, imgWidth)
                pass
                newImg = img.crop(cropContent)
                # 缩略图大小
                thumbnailSize = (240 if newImg.width > 240 else newImg.width, 240 if newImg.height > 240 else newImg.height)
                newImg.thumbnail(thumbnailSize)
                newImg.save(os.path.join(filePath, fileName + '_square1200.' + fileExt))
            pass
            img.thumbnail(middleSize)
            img.save(os.path.join(filePath, fileName + '_master1200.' + fileExt))
        pass
        return item
    pass
pass

class PixivUserPipeline(object):

    def __init__(self,dbpool):
        self.dbpool = dbpool
        self.headimgs = []
    pass

    @classmethod
    def from_crawler(cls, crawler):
        parmas = {
            'host': crawler.settings['MYSQL_SETTINGS']['host'],
            'user': crawler.settings['MYSQL_SETTINGS']['user'],
            'password': crawler.settings['MYSQL_SETTINGS']['password'],
            'db': crawler.settings['MYSQL_SETTINGS']['db'],
            'port': crawler.settings['MYSQL_SETTINGS']['port'],
            'charset': crawler.settings['MYSQL_SETTINGS']['charset'],
        }

        dbpool = adbapi.ConnectionPool(
            'pymysql',
            **parmas
        )
        return cls(dbpool)
    pass

    def process_item(self, item, spider):
        if isinstance(item, PixivUserItem):
            self.headimgs.append({
                'url': item['profile_img_origin'],
                'user_id': item['id']
            })
            
            query = self.dbpool.runInteraction(
                self.insert_data_todb,
                item,
                spider
            )
        
            query.addErrback(
                self.handle_error,
                item
            )
        pass
        return item
    pass

    def insert_data_todb(self,cursor,item,spider):
        sql = 'INSERT INTO user(id, user_create_time, user_name, user_comment, user_comment_html, follows, user_account, user_sex, location, user_country, cover_image, profile_img_main, profile_img_main_s, social_pawoo_url, social_twitter_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (item['id'], item['user_create_time'], item['user_name'], item['user_comment'], item['user_comment_html'], item['follows'], item['user_account'], item['user_sex'], item['location'], item['user_country'], item['cover_image'], item['profile_img_main'], item['profile_img_main_s'], item['social_pawoo_url'], item['social_twitter_url']))
        print('插入成功')
    pass

    def handle_error(self,failure,item):
        print(failure)
        print('插入错误')
    pass

    def close_spider(self, spider):
        if len(self.headimgs) > 0:
            with open('headimgs.json', 'w', encoding = 'utf-8') as f:
                f.write(json.dumps(self.headimgs))
            pass
        pass
        self.dbpool.close()
    pass
pass