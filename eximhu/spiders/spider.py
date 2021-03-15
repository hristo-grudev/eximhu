import scrapy
from scrapy import Selector
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader

from ..items import EximhuItem
from itemloaders.processors import TakeFirst

import requests

url = "https://exim.hu/component/bdthemes_shortcodes/?view=post&layout=default"

payload = "source=category%3A+29%2C145" \
          "&limit=12" \
          "&layout=grid" \
          "&show_more=yes" \
          "&intro_text_limit=105" \
          "&show_more_item=12" \
          "&show_more_action=click" \
          "&order=created" \
          "&order_by=desc" \
          "&loading_animation=sequentially" \
          "&filter_animation=rotateSides" \
          "&caption_style=overlayBottomPush" \
          "&horizontal_gap=35" \
          "&vertical_gap=15" \
          "&filter=yes" \
          "&filter_style=2" \
          "&filter_deeplink=false" \
          "&filter_align=" \
          "&filter_counter=yes" \
          "&category=yes&date=yes" \
          "&large=4" \
          "&medium=3" \
          "&small=1" \
          "&show_thumb=yes" \
          "&thumb_resize=yes" \
          "&include_article_image=yes" \
          "&thumb_width=640" \
          "&thumb_height=480" \
          "&show_search=no" \
          "&scroll_reveal=" \
          "&class=" \
          "&offset={}" \
          "&numberOfClicks={}"
headers = {
  'authority': 'exim.hu',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': 'text/html, */*; q=0.01',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://exim.hu',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '0392b112e6d7ce28fd0b5a97e9e09376=9f4a5948e57d1053a55acf0b3b657aa6; nrid=bf452f9b0cc08bf1; cookieconsent_status=allow; rl_modals=3; _ga=GA1.2.391037891.1615808770; _gid=GA1.2.1942141679.1615808770'
}


class EximhuSpider(scrapy.Spider):
	name = 'eximhu'
	start_urls = ['https://exim.hu/sajtoszoba/hirek-sajtokozlemenyek']
	page = 0
	click = 0

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload.format(self.page, self.click))
		more_posts = Selector(text=data.text).xpath('//div[contains(@class, "cbp-item")]')
		for post in more_posts:
			link = post.xpath('.//a[@class="cbp-l-grid-blog-title"]/@href').get()
			date = post.xpath('.//span[@class="cbp-l-grid-blog-date"]/text()').get()
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date})

		if more_posts:
			self.page += 12
			self.click += 1
			yield response.follow(response.url, self.parse, dont_filter=True)
		else:
			raise CloseSpider('No more pages')

	def parse_post(self, response, date):
		title = response.xpath('//h1[@property="headline"]/text()').get()
		description = response.xpath('//div[@class="uk-margin-medium-top"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=EximhuItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
