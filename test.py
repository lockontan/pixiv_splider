import datetime
from pixivUtils import writeErrorLog, getBeforeDate
def getdate(beforeOfDay):
  today = datetime.datetime.now()
  # 计算偏移量
  offset = datetime.timedelta(days=-beforeOfDay)
  # 获取想要的日期的时间
  re_date = (today + offset).strftime('%Y-%m-%d')
  return re_date
print(getdate(5))

if not False:
	print(11)
pass