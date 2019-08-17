from pixivUrl import pixivUrl
from pixivUtils import writeErrorLog, getBeforeDate
from pixivConfig import pixivConfig
import time
import configparser

url = pixivUrl()

isUpdate = False
while isUpdate == False:
	isUpdate = url.getUpdate()
	if not isUpdate:
		time.sleep(60)
	pass
pass

writeErrorLog('排行已更新，开始下载')

# 更新排行日期
def updateRankDate():
	__config__ = pixivConfig()
	conf = configparser.ConfigParser()

	conf.add_section('date')
	conf.set('date', 'update', getBeforeDate(1))
	# 写入文件
	with open(__config__.rank['updatePath'], 'r+')as conffile:
	    conf.write(conffile)
	pass
pass

# 开始下载
time.sleep(10)
for page in range(10):
 	url.requestsRankUrl('daily', 'illust', '', page + 1)
 	url.requestsRankUrl('weekly', 'illust', '', page + 1)
 	url.requestsRankUrl('monthly', 'illust', '', page + 1)
 	if page == 0:
 		updateRankDate()
 	pass
pass
