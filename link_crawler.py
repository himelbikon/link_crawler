from bs4 import BeautifulSoup as bs
from datetime import datetime
from threading import Thread
import requests, os


class Crawler:
	def __init__(self, host, threading_limit):
		self.host = host
		self.threading_limit = threading_limit
		self.all_urls = set()
		self.done_urls = set()
		self.pend_urls = set()
		self.ext_urls = set()
		self.path = self.host.split('//')[1]
		self.counter = 0

	def request(self, url):
		try:
			return requests.get(url)
		except:
			pass

	def pre_printer(self):
		self.s = '----------'
		print(self.s, 'Starting', self.s)

	def post_printer(self):
		print(self.s, 'Ending', self.s)
		time = datetime.now().replace(microsecond=0) - self.starting_time
		print('Time Duration:', time)

	def preparation(self):
		if os.path.exists(self.path + '/all_urls.txt'):
			yes = input(self.host + ' has previous data. Do you want to load it?\n--> ')
			if yes.lower() == 'yes' or yes.lower() == 'y':
				file = open(self.path + '/all_urls.txt', 'r', encoding="utf-8")
				self.all_urls = set(file.read().split('\n'))
				file.close()

				file = open(self.path + '/ext_urls.txt', 'r', encoding="utf-8")
				self.ext_urls = set(file.read().split('\n'))
				file.close()
			else:
				self.all_urls.add(self.host)
		else:
			self.all_urls.add(self.host)

	def printer(self, link):
		print(f'[{len(self.all_urls)}]', link)

	def status(self, pend):
		print('[', self.s, 'Pending:', pend, self.s, ']')

	def file_writer(self, name, urls):
		urls = '\n'.join(urls)
		if not os.path.exists(self.path):
			os.mkdir(self.path)
		file = open(self.path + '/' + name + '.txt', 'w', encoding="utf-8")
		file.write(urls)
		file.close()

	def temp_saver(self):
		self.file_writer('all_urls', self.all_urls)
		if len(self.ext_urls) > 0:
			self.file_writer('ext_urls', self.ext_urls)

	def saver(self):
		self.file_writer('Internal_urls', self.all_urls)
		if len(self.ext_urls) > 0:
			self.file_writer('External_urls', self.ext_urls)

	def manager(self, urls):
		if len(urls) >= self.threading_limit:
			holder = {}
			for i in range(self.threading_limit):
				target_url = urls.pop()
				holder[i] = Thread(target=lambda: self.extractor(target_url))
				holder[i].start()
			for j in range(self.threading_limit):
				holder[j].join()
		else:
			for url in urls:
				self.extractor(url)

	def corrector(self, link):
		link = link.split('&')[0].strip()
		link = link.split('#')[0].strip()
		if len(link) > 0:
			if link[0] == '/':
				if host[-1] == '/':
					link = host[0:-1] + link
				else:
					link = host + link
		return link

	def extractor(self, url):
		response = self.request(url)
		if response:
			source_code = response.text
			soup = bs(source_code, 'lxml')
			anchors = soup.find_all('a')
			if len(anchors) > 0:
				for anchor in anchors:
					link = anchor.get('href')
					if link and 'http' in link:
						link = self.corrector(link)
						if host[2:-2] in link:
							if link not in self.all_urls:
								self.all_urls.add(link)
								self.printer(link)
						else:
							self.ext_urls.add(link)
		self.done_urls.add(url)


	def crawl(self):
		self.pre_printer()
		self.starting_time = datetime.now().replace(microsecond=0)
		self.preparation()

		while True:
			self.pend_urls = self.all_urls - self.done_urls
			self.status(len(self.pend_urls))

			if len(self.all_urls) - self.counter >= 2000:
				self.temp_saver()
				self.counter = len(self.all_urls)

			if len(self.pend_urls) <= 0:
				break

			self.manager(self.pend_urls)

		
		self.saver()
		self.post_printer()



host = input('Enter URL: ')
threading_limit = int(input('Enter Threading Limit: '))

crawler = Crawler(host, threading_limit)
crawler.crawl()

