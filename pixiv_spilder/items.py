# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class PixivRankItem(scrapy.Item):
    # 排行类型
    mode = scrapy.Field()
    # 作品类别
    content = scrapy.Field()
    # 作者id
    user_id = scrapy.Field()
    # 作品id
    illust_id = scrapy.Field()
    # 排名
    rank = scrapy.Field()
    # 排行日期
    date = scrapy.Field()
pass

class PixivIllustItem(scrapy.Item):
    # 作品id
    id = scrapy.Field()
    # 作者id
    user_id = scrapy.Field()
    # 作品题目
    title = scrapy.Field()
    # 上传时间
    upload_timestamp = scrapy.Field()
    comment = scrapy.Field()
    comment_html = scrapy.Field()
    bookmark_user_total = scrapy.Field()
    rating_count = scrapy.Field()
    rating_view = scrapy.Field()
    # 是否限制
    x_restrict = scrapy.Field()
    # 作品类型 1 插画 2漫画 3动图
    type = scrapy.Field()
    # 爬取日期
    created = scrapy.Field()
    # 图片列表
    imgs = scrapy.Field()
    # 作品标签
    tags = scrapy.Field()
pass

class PixivImgItem(scrapy.Item):
    # 图片存储全路径
    path = scrapy.Field()
    # 图片张数
    page = scrapy.Field()
    # 图片所属作品id
    id = scrapy.Field()
pass

class PixivUserItem(scrapy.Item):
    # 作者id
    id = scrapy.Field()
    user_create_time = scrapy.Field()
    # 昵称
    user_name = scrapy.Field()
    # 自我介绍
    user_comment = scrapy.Field()
    user_comment_html = scrapy.Field()
    follows = scrapy.Field()
    user_account = scrapy.Field()
    # 性别
    user_sex = scrapy.Field()
    # 地区
    location = scrapy.Field()
    # 国家
    user_country = scrapy.Field()
    # 主页封面
    cover_image = scrapy.Field()
    # 原始头像链接
    profile_img_origin = scrapy.Field()
    # 头像
    profile_img_main = scrapy.Field()
    profile_img_main_s = scrapy.Field()
    # 社交主页
    social_pawoo_url = scrapy.Field()
    social_twitter_url = scrapy.Field()
pass