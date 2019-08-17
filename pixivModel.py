from pixivDb import dbCursor
from pixivUtils import isChTag, writeErrorLog, getFileName, getFileExt
import html
import json
import os
from pixivDownload import pixivDownload
import traceback
import requests
import pixivConfig
import time
import random
import re

__config__ = pixivConfig.pixivConfig()

# user model
class pixivUser(object):
	"""docstring for pixivUser"""

	def __init__(self, data):
		super(pixivUser, self).__init__()

		modelData = {}
		modelData['id'] = str(data.get('user_id'))
		modelData['user_create_time'] = data.get('user_create_time' or '')
		modelData['user_name'] = data.get('user_name' or '')
		modelData['user_comment'] = html.escape(data.get('user_comment' or ''))
		modelData['user_comment_html'] = html.escape(data.get('user_comment_html' or ''))
		modelData['follows'] = data.get('follows' or '0')
		modelData['user_account'] = data.get('user_account' or '0')
		modelData['user_sex'] = data.get('user_sex') or '3'
		modelData['location'] = data.get('location' or '')
		modelData['user_country'] = data.get('user_country' or '')

		if data['cover_image']:
			modelData['cover_image'] = 'https://i.pximg.net/c/background/img' + data['cover_image']['profile_cover_filename'] + '.' + data['cover_image']['profile_cover_ext']
		pass

		if data.get('profile_img'):
			self.headimg = data['profile_img']['main']
			modelData['profile_img_main'] = '/pixiv/headimg/' + modelData['id'] + '_head' + os.path.splitext(data['profile_img']['main'])[1]
			modelData['profile_img_main_s'] = data['profile_img']['main_s']
		pass

		if data.get('social'):
			keys = data['social'].keys()
			if 'pawoo' in keys:
				modelData['social_pawoo_url'] = data['social']['pawoo']['url']
			pass
			if 'twitter' in keys:
				modelData['social_twitter_url'] = data['social']['twitter']['url']
			pass
		pass

		self.modelData = modelData
	pass

	def insertDb(self):
		try:
			dbCursor.execute("SELECT * FROM user WHERE id = " + self.modelData['id'])
			items = self.modelData.items()
			key = [i[0] for i in items]
			item = ["'" + re.sub(r"'", "''", str(i[1])) + "'" for i in items]
			dbCursor.execute("INSERT INTO user(" + ','.join(key) + ") VALUES (" + ','.join(item) + ")")
			writeErrorLog('当前用户： ' + str(self.modelData['id']) + '已写入数据库')
		except Exception as e:
			error = open('errorUser.txt', 'a', encoding = 'utf-8')
			error.write(self.modelData['id'] + '\n')
			writeErrorLog('当前用户： ' + str(self.modelData['id']) + '写入数据库失败, ' + traceback.format_exc())
		pass
	pass

	def downloadHeadImg(self):
		try:
			res = requests.get(self.headimg, proxies = __config__.proxies, headers = {'referer': 'https://www.pixiv.net/member.php?id=' + str(self.modelData['id'])})
			if res.status_code == 200:
				fileName = self.modelData['id'] + '_head' + os.path.splitext(self.headimg)[1]
				filePath = __config__.download['baseHeadPath']
				fullPath = os.path.join(filePath, fileName)

				if os.path.exists(filePath) == False :
					os.makedirs(filePath)
				pass

				fp = open(fullPath, 'wb')
				fp.write(res.content)
				fp.close()
				writeErrorLog('当前头像： ' + str(self.modelData['id']) + '下载成功')
			else:
				raise Exception('res_code: ' + str(res.status_code))
			pass
		except requests.exceptions.RequestException as e:
			raise Exception('头像请求失败')
		except Exception as e:
			error = open('errorHeadimg.txt', 'a', encoding = 'utf-8')
			error.write(self.modelData['id'] + ' ' + self.headimg + '\n')
			writeErrorLog('当前头像： ' + str(self.modelData['id']) + '下载失败, ' + traceback.format_exc())
		pass
	pass
pass


# article model
class pixivArticle(object):
	"""docstring for pixivArticle"""

	def __init__(self, data):
		super(pixivArticle, self).__init__()
		self.imgs = []

		modelData = {}
		modelData['id'] = str(data.get('id'))
		modelData['user_id'] = str(data.get('user_id'))
		modelData['title'] = data.get('title' or '')
		modelData['upload_timestamp'] = data.get('upload_timestamp' or '')
		modelData['comment'] = html.escape(data.get('comment') or '')
		modelData['comment_html'] = html.escape(data.get('comment_html') or '')
		modelData['bookmark_user_total'] = data.get('bookmark_user_total' or '')
		modelData['rating_count'] = data.get('rating_count' or '')
		modelData['rating_view'] = data.get('rating_view' or '')
		modelData['x_restrict'] = data.get('x_restrict' or '')
		modelData['type'] = data.get('type' or '')

		imgs = []
		imgPath = '/pixiv/img/' + str(data.get('id'))
		if 'manga_a' in data :
			self.imgs = data.get('manga_a') or []
			for index in range(len(data['manga_a'])):
				item = data['manga_a'][index]
				otherItem = data['illust_images'][index]
				ext = getFileExt(data['url_big'])
				imgs.append({
					'page': index,
					'url': '/'.join([imgPath, modelData['id'] + '_p' + str(index) + '_master1200' + ext]),
					'url_big': '/'.join([imgPath, modelData['id'] + '_p' + str(index) + ext]),
					'url_small': '/'.join([imgPath, modelData['id'] + '_p' + str(index) + '_square1200' + ext]),
					'width': otherItem['illust_image_width'],
					'height': otherItem['illust_image_height'],
				})
			pass
		else:
			self.imgs = [{
				'page': 0,
				'url_big': data['url_big']
			}]
			ext = getFileExt(data['url_big'])
			fileName = getFileName(data['url_big'])
			imgs.append({
				'page': 0,
				'url': '/'.join([imgPath, modelData['id'] + '_p0' + '_master1200' + ext]),
				'url_big': '/'.join([imgPath, modelData['id'] + '_p0' + ext]),
				'url_small': '/'.join([imgPath, modelData['id'] + '_p0' + '_square1200' + ext]),
				'width': data['width'],
				'height': data['height'],
			})
		pass
		modelData['imgs'] = json.dumps(imgs)

		tags = []
		if 'display_tags' in data:
			for item in data['display_tags']:
				tag = ''
				if 'translation' in item:
					if isChTag(str(item.get('translation'))) :
						tag = item.get('translation')
					else:
						tag = item.get('tag')
					pass
				else:
					tag = item.get('tag')
				pass
				tags.append(tag)
			pass
		pass
		# 去重
		tags = list(set(tags))
		if len(tags) > 0:
			modelData['tags'] = ',' + ','.join(tags) + ','
		pass

		self.modelData = modelData
	pass

	def insertDb(self):
		try:
			items = self.modelData.items()
			key = [i[0] for i in items]
			item = ["'" + re.sub(r"'", "''", str(i[1])) + "'" for i in items]
			dbCursor.execute("INSERT INTO illust(" + ','.join(key) + ") VALUES (" + ','.join(item) + ")")
			writeErrorLog('当前作品： ' + str(self.modelData['id']) + '已写入数据库')
		except Exception as e:
			error = open('errorArticle.txt', 'a', encoding = 'utf-8')
			error.write(self.modelData['id'] + '\n')
			writeErrorLog('当前作品： ' + str(self.modelData['id']) + '写入数据库失败, ' + traceback.format_exc())
		pass
	pass

	def downloadImg(self):
		downloadImg = pixivDownload().downloadImg
		for i in range(len(self.imgs)):
			item = self.imgs[i]
			ext = getFileExt(item['url_big'])
			downloadImg(item['url_big'], self.modelData['id'], str(self.modelData['id']) + '_p' + str(i) + ext)
		pass
	pass
pass

# rank model
class pixivRank(object):
	"""docstring for pixivRank"""
	def __init__(self, data, mode, content):
		super(pixivRank, self).__init__()
		modelData = {}
		modelData['mode'] = mode
		modelData['content'] = content
		modelData['user_id'] = data['user_id']
		modelData['illust_id'] = data['illust_id']
		modelData['rank'] = data['rank']
		modelData['yes_rank'] = data['yes_rank']
		modelData['date'] = data['date']
		self.modelData = modelData
	pass

	def insertDb(self):
		try:
			items = self.modelData.items()
			key = [i[0] for i in items]
			item = ["'" + re.sub(r"'", "''", str(i[1])) + "'" for i in items]
			dbCursor.execute("INSERT INTO ranking(" + ','.join(key) + ") VALUES (" + ','.join(item) + ")")
		except Exception as e:
			error = open('errorRanking.txt', 'a', encoding = 'utf-8')
			error.write(json.dumps(self.modelData) + '\n')
			writeErrorLog('当前排行： 写入数据库失败, ' + json.dumps(self.modelData) + ', ' + traceback.format_exc())
		pass
	pass
pass
