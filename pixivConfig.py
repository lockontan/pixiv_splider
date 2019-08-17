# load config
import configparser

class pixivConfig(object):

	def __init__(self):
		super(pixivConfig, self).__init__()
		self.loadConfig()
	pass

	def loadConfig(self):
		config = configparser.ConfigParser()
		config.read('./config.ini', encoding='utf8')

		if config.get('proxies', 'openProxy') == 'True':
			self.proxies = {
				'https': config.get('proxies', 'https'),
				'http': config.get('proxies', 'http')
			}
		else:
			self.proxies = {}
		pass
		self.referer = {
			'dailyIllust': config.get('referer', 'dailyIllust'),
		}

		self.download = {
			'basePath': config.get('download', 'basePath'),
			'baseHeadPath': config.get('download', 'baseHeadPath'),
		}

		self.log = {
			'path': config.get('log', 'path')
		}

		self.rank = {
			'updatePath': config.get('rank', 'updatePath')
		}
	pass
pass