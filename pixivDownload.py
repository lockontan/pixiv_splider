import pixivConfig
import os
import time
from PIL import Image
from pixivUserAgent import getUserAget
from pixivUtils import writeErrorLog
import requests
import traceback

__config__ = pixivConfig.pixivConfig()

class pixivDownload():
	__retry_times = 0

	def __init__(self):
		super(pixivDownload, self).__init__()
	pass

	def downloadImg(self, url, id, fileNameWithExt):
		headers = {
			'referer': 'https://www.pixiv.net/member_illust.php?mode=big&illust_id=' + str(id),
		  'user-agent': getUserAget()
		}
		try:
			res = requests.get(url, proxies = __config__.proxies, headers = headers)
			if res.status_code == 200:
				filePath = os.path.join(__config__.download['basePath'], str(id))

				if os.path.exists(filePath) == False :
					os.makedirs(filePath)
				pass

				fullPath = os.path.join(filePath, fileNameWithExt)

				fp = open(fullPath, 'wb')
				fp.write(res.content)
				fp.close()
				self.getThumbnailAndMiddleImg(fullPath, fileNameWithExt)
				writeErrorLog('当前作品： ' + str(id) + '下载成功'+ ', url: ' + url)
			pass
		except requests.exceptions.RequestException as e:
			if self.__retry_times < 5:
				time.sleep(20)
				self.__retry_times = self.__retry_times + 1
				self.downloadImg(url, id)
			else:
				error = open('errorDownload.txt', 'a', encoding = 'utf-8')
				error.write(str(id) + '\n')
				writeErrorLog('当前作品： ' + str(id) + '下载失败，已写入errorDownload.txt'+ ', url: ' + url)
			pass
		except Exception as e:
			error = open('errorDownload.txt', 'a', encoding = 'utf-8')
			error.write(str(id) + '\n')
			writeErrorLog('当前作品： ' + str(id) + '下载失败，已写入errorDownload.txt' + ', url: ' + url + ', ' + traceback.format_exc())
		pass
	pass

	def getThumbnailAndMiddleImg(self, path, fileNameWithExt):
		fullName = fileNameWithExt
		fileName = fullName.split('.')[0]
		fileExt = fullName.split('.')[1]
		filePath = os.path.dirname(path)

		img = Image.open(path)
		imgWidth = img.width
		imgHeight = img.height

		# 缩略图大小
		thumbnailSize = (240, 240)
		# 中等图大小
		middleSize = (600, 600 / imgWidth * imgHeight)

		# 图片剪裁区域
		cropContent = (0, 0, imgWidth, imgHeight)
		if imgWidth > imgHeight:
			cropContent = (0, 0, imgHeight, imgHeight)
		elif imgWidth < imgHeight:
			cropContent = (0, 0, imgWidth, imgWidth)
		pass
		newImg = img.crop(cropContent)
		if newImg.width > 240:
			newImg.thumbnail(thumbnailSize)
		pass
		newImg.save(os.path.join(filePath, fileName + '_square1200.' + fileExt))
		img.thumbnail(middleSize)
		img.save(os.path.join(filePath, fileName + '_master1200.' + fileExt))
	pass
pass

# d = pixivDownload()
# d.downloadImg('https://i.pximg.net/img-original/img/2019/07/28/00/00/02/75941714_p0.jpg', 75941714)
		