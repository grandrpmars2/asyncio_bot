import requests
from bs4 import BeautifulSoup
import lxml
import csv
import aiohttp
import asyncio

games_data = []

async def get_data(session, page):
	headers = {
		'user-agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
	}
	url = f'https://stopgame.ru/review/new/izumitelno/p{page}'

	async with session.get(url, headers=headers) as response:
		soup = BeautifulSoup(await response.text(), 'lxml')
		cards = soup.find_all('div', class_='item article-summary')

		for card in cards:
			game_title = card.find('div', class_='caption caption-bold').find('a').text.replace(': Обзор', '')
			game_url = 'https://stopgame.ru' + str(card.find('div', class_='caption caption-bold').find('a').get('href'))

				# request to get views and comments number from game page
			async with session.get(game_url, headers=headers) as response:
				soup = BeautifulSoup(await response.text(), 'lxml')

				comments = soup.find('a', class_='comments-link').text
				views = soup.find_all('div', class_='article-info-item')[-1].text.strip(' ')

				games_data.append(
					{
					'Game title'      : game_title,
					'Comments number' : comments,
					'Views number'    : views,
					'Url'             : game_url
					}
				)

		print(f'[INFO] Обработал страницу {page}')

async def gather_data():
	headers = {
		'user-agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
	}
	url = 'https://stopgame.ru/review/new/izumitelno'

	async with aiohttp.ClientSession() as session:
		response = await session.get(url, headers=headers)
		soup = BeautifulSoup(await response.text(), 'lxml')

		all_pages = soup.find('span', class_='pages')
		max_page = int(all_pages.find_all('a', class_='item')[-1].text)

		tasks = []

		for page in range(1, max_page + 1):
			task = asyncio.create_task(get_data(session, page))
			tasks.append(task)

		await asyncio.gather(*tasks)

def main():
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	asyncio.run(gather_data())

	with open('data.csv', 'w', newline = '') as file:
		writer = csv.writer(file, delimiter=' ')
		writer.writerow(
			(
			'Game title',
			'Comments number',
			'Views number',
			'Url'
			)
		)

	for game in games_data:
		with open('data.csv', 'a', newline = '', encoding = 'utf-8') as file:
			writer = csv.writer(file, delimiter = ' ')
			writer.writerow(
				(
					game['Game title'],
					game['Comments number'],
					game['Views number'],
					game['Url']
				)
			)

if __name__ == '__main__':
	main()