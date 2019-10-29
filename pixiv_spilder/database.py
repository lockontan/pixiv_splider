import pymysql

from pixiv_spilder.settings import MYSQL_SETTINGS

db = pymysql.connect(
    host = MYSQL_SETTINGS['host'],
    user = MYSQL_SETTINGS['user'],
    password = MYSQL_SETTINGS['password'],
    db = MYSQL_SETTINGS['db'],
    port = MYSQL_SETTINGS['port'],
    charset = MYSQL_SETTINGS['charset'],
    cursorclass = pymysql.cursors.DictCursor
)
