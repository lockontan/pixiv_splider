import pixivConfig
from pixivUserAgent import getUserAget
from pixivUtils import qsStringify, urlParse, urlPath, writeErrorLog, getBeforeDate
from pixivModel import pixivUser, pixivArticle, pixivRank
from pixivDb import dbCursor

import time
import random
import json
from urllib import parse
import requests
import traceback

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False

__config__ = pixivConfig.pixivConfig()

class pixivUrl(object):
	time = 0
	def __init__(self):
		super(pixivUrl, self).__init__()
		self.urls = []
	pass

	# 排行是否更新
	def getUpdate(self):
		url = 'https://www.pixiv.net/touch/ajax_api/ajax_api.php?mode=ranking&mode_rank=daily&date=&content=illust&p=1'
		referer = __config__.referer['dailyIllust']
		isUpdate = False
		try:
			res = requests.get(url, proxies = __config__.proxies, headers = {'user-agent': getUserAget(), 'referer': referer}, timeout = 10)
			res.encoding = 'utf-8'  
			if res.status_code == 200:
				resJson = json.loads(res.text)
				if len(resJson):
					data = resJson[0]
					isUpdate = data['date'] == getBeforeDate(1)
				pass
			else:
				raise Exception('res_code: ' + str(res.status_code))
			pass
		except requests.exceptions.RequestException as e:
			writeErrorLog('getUpdate: 请求出错')
		except Exception as e:
			writeErrorLog('getUpdate: 其他出错, ' + traceback.format_exc())
		pass
		return isUpdate
	pass

	def requestsRankUrl(self, mode, content, date, page):
		baseUrl = 'https://www.pixiv.net/touch/ajax_api/ajax_api.php'
		referer = __config__.referer['dailyIllust']
		if page > 1:
			referer = referer + '&p=' + str(page - 1)
		pass
		fullUrl = baseUrl + '?' + qsStringify({'mode': 'ranking', 'mode_rank': mode, 'content_rank': content, 'p': page, 'date': date})
		try:
			writeErrorLog('mode: ' + mode + ' page: ' + str(page))
			res = requests.get(fullUrl, proxies = __config__.proxies, headers = {'user-agent': getUserAget(), 'referer': referer}, timeout = 10)
			res.encoding = 'utf-8'  
			if res.status_code == 200:
				resJson = json.loads(res.text)
				for item in resJson:
					if item.get('user_id') and item.get('illust_id'):
						rankModel = pixivRank(item, mode, content)
						rankModel.insertDb()
						time.sleep(0.5)

						dbCursor.execute("SELECT * FROM user WHERE id = " + item['user_id'])
						if not dbCursor.fetchall():
							self.requestsUser(item['user_id'])
							time.sleep(random.randint(5, 10))
						else:
							writeErrorLog('当前用户： ' + str(item['user_id']) + '已存在')
							time.sleep(0.5)
						pass

						dbCursor.execute("SELECT * FROM illust WHERE id = " + item['illust_id'])
						if not dbCursor.fetchall():
							artRefer = 'https://www.pixiv.net/ranking.php?mode='+ mode +'&content='+ content +'&p=' + str(page)
							artUrl = 'https://www.pixiv.net/touch/ajax/illust/details?illust_id=' + str(item['illust_id']) + '&ref=' + artRefer
							self.requestsArticle(artUrl, item['illust_id'])
							time.sleep(random.randint(5, 10))
						else:
							writeErrorLog('当前作品： ' + str(item['illust_id']) + '已存在')
							time.sleep(0.5)
						pass
					pass
				pass
			else:
				raise Exception('res_code: ' + str(res.status_code))
			pass
		except requests.exceptions.RequestException as e:
			writeErrorLog('requestsRankUrl: 连接url: ' + fullUrl + ' 出错, 20s后重试')
			self.time = self.time + 1
			if self.time < 5:
				time.sleep(random.randint(5, 10))
				self.requestsRankUrl(mode, content, date, page)
			else:
				self.time = 0
			pass
		except Exception as e:
			writeErrorLog('requestsRankUrl: ' + 'fullUrl, ' + traceback.format_exc())
		pass
	pass

	def requestsUser(self, userId):
		url = 'https://www.pixiv.net/touch/ajax/user/details?id=' + userId
		try:
			res = requests.get(url, proxies = __config__.proxies, headers = {'user-agent': getUserAget(), 'referer': url})
			res.encoding = 'utf-8'  
			if res.status_code == 200:
				resJson = json.loads(res.text)
				if 'user_details' in resJson:
					userModel = pixivUser(resJson['user_details'])
					userModel.downloadHeadImg()
					userModel.insertDb()
				pass
			else:
				raise Exception('res_code: ' + str(res.status_code))
			pass
		except requests.exceptions.RequestException as e:
			writeErrorLog('requestsUser: 连接url: ' + url + ' 出错, 20s后重试')
			self.time = self.time + 1
			if self.time < 5:
				time.sleep(random.randint(5, 10))
				self.requestsUser(userId)
			else:
				self.time = 0
			pass
		except Exception as e:
			writeErrorLog('requestsUser: ' + 'url, ' + traceback.format_exc())
		pass
	pass

	def requestsArticle(self, url, articleId):
		referer = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(articleId)
		try:
			res = requests.get(url, proxies = __config__.proxies, headers = {'user-agent': getUserAget(), 'referer': referer, 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'})
			res.encoding = 'utf-8'  
			if res.status_code == 200:
				resJson = json.loads(res.text)
				if 'body' in resJson:
					articleModel = pixivArticle(resJson['body']['illust_details'])
					articleModel.downloadImg()
					articleModel.insertDb()
				pass
			else:
				raise Exception('res_code: ' + str(res.status_code))
			pass
		except requests.exceptions.RequestException as e:
			writeErrorLog('requestsArticle: 连接url: ' + url + ' 出错, 20s后重试')
			self.time = self.time + 1
			if self.time < 5:
				time.sleep(random.randint(5, 10))
				self.requestsArticle(url, articleId)
			else:
				self.time = 0
			pass
		except Exception as e:
			writeErrorLog('requestsArticle:'+ 'url, ' + traceback.format_exc())
		pass
	pass
pass
