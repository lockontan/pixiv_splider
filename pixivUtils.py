from urllib.parse import urlencode
from urllib.parse import parse_qs, urlparse
import pixivConfig

import datetime
import os
import re

def qsStringify(object):
	return urlencode(object)
pass

def urlParse(url):
	query = urlparse(url).query
	params = parse_qs(query)
	result = {key: params[key][0] for key in params}
	return result
pass

def urlPath(url):
	result = urlparse(url)
	return result.scheme + '://' + result.netloc + result.path
pass

def isChTag(s):
	for ch in s:
		if '\u4e00' <= ch <= '\u9fa5':
			return True
		pass
	pass
	return False
pass

# write error log
def writeErrorLog(msg):
	__config__ = pixivConfig.pixivConfig()
	date = datetime.datetime.now().strftime('%Y-%m-%d')
	logName = __config__.log['path'] + date + '-log.txt'
	error = open(logName, 'a', encoding = 'utf-8')

	currentDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	error.write(currentDate + ' ' + msg + '\n')
pass

# 获取文件名
def getFileName(path):
	ext = os.path.splitext(path)[1]
	filename = os.path.basename(path)
	name = re.sub(ext, "", filename)
	return name
pass

# 获取文件名扩展名
def getFileExt(path):
	return os.path.splitext(path)[1]
pass

# 获取前几天日期
def getBeforeDate(beforeOfDay):
  today = datetime.datetime.now()
  # 计算偏移量
  offset = datetime.timedelta(days=-beforeOfDay)
  # 获取想要的日期的时间
  re_date = (today + offset).strftime('%Y-%m-%d')
  return re_date
pass
