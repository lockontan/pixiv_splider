from pixiv_spilder.items import PixivRankItem
from urllib.parse import urlencode
import json
import scrapy

class rankSpider(scrapy.Spider):
    name = 'rank'
    date = ''
    baseUrl = 'https://www.pixiv.net/touch/ajax_api/ajax_api.php?'

    def start_requests(self):
        urls = [
            { 'mode': 'daily', 'page': '1', 'content': 'illust', 'date': self.date},
            { 'mode': 'weekly', 'page': '1', 'content': 'illust', 'date': self.date},
            { 'mode': 'monthly', 'page': '1', 'content': 'illust', 'date': self.date},
            { 'mode': 'male', 'page': '1', 'content': 'all', 'date': self.date},
            { 'mode': 'original', 'page': '1', 'content': 'all', 'date': self.date},
            { 'mode': 'rookie', 'page': '1', 'content': 'illust', 'date': self.date},
        ]
        for item in urls:
            url = self.baseUrl + urlencode({'mode': 'ranking', 'mode_rank': item['mode'], 'content_rank': item['content'], 'p': item['page'], 'date': item['date']})
            yield scrapy.Request(url = url, meta = item, callback = self.parseRank)
        pass
    pass

    def parseRank(self, response):
        resJson = json.loads(response.body.decode('utf-8'))
        resMeta = response.meta
        for item in resJson:
            rank_item = PixivRankItem()
            rank_item['mode'] = resMeta['mode']
            rank_item['content'] = resMeta['content']
            rank_item['user_id'] = item.get('user_id')
            rank_item['illust_id'] = item.get('illust_id')
            rank_item['rank'] = item.get('rank')
            rank_item['date'] = item.get('date')
            yield rank_item
        pass
        newPage = int(resMeta['page']) + 1
        if newPage <= 10:
            resMeta['page'] = str(newPage)
            url = self.baseUrl + urlencode({'mode': 'ranking', 'mode_rank': resMeta['mode'], 'content_rank': resMeta['content'], 'p': resMeta['page'], 'date': resMeta['date']})
            yield scrapy.Request(url = url, meta = resMeta, callback = self.parseRank)
        pass
    pass
pass
