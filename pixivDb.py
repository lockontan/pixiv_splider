import pymysql

connection = pymysql.connect(
	host = 'localhost',
	user = 'root',
	password = '123456',
	db = 'pixiv',
	charset = 'utf8mb4',
	cursorclass = pymysql.cursors.DictCursor
)

dbCursor = connection.cursor()
