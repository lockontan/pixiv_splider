import os
os.system("cd /var/www/pixiv_spilder && python3 -m scrapy crawl rank && python3 -m scrapy crawl illust && python3 -m scrapy crawl user && python3 -m scrapy crawl img && python3 -m scrapy crawl headimg")
