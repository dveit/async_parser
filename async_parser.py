import time
from bs4 import BeautifulSoup
import csv
import asyncio
import aiohttp


def dt_corrector(dt):
    return dt.replace('T', ' ').split()


async def gather_data():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
        }
    url = 'https://1news.az/lenta/'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        pages_count = int(soup.find('div', class_='pagination').find('a', class_='last')\
            .get('href').replace('https://1news.az/lenta/?page=', ''))

        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


news_data = []


async def get_page_data(session, page):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
        }
    url = f'https://1news.az/lenta/?page={page}'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')
        news_list = soup.find('div', class_='newsList').find_all('a')

        for news in news_list:
            release_date_tag = news.find('time', class_='date')
            rdate, rtime = dt_corrector(release_date_tag['datetime'])
            title = news.find('span', class_='title').text
            url = 'https://1news.az/lenta' + news.get('href')

            news_data.append( {'rdatetime': rdate + ' ' + rtime,
                    'rtime': rtime,
                    'title': title,
                    'url': url
                    }
            )


start_time = time.time()


def main():
    asyncio.run(gather_data())
    for news in news_data:
        with open('1news.csv', 'a') as file:
            writer = csv.writer(file)

            writer.writerow((news['rdatetime'],
                             news['title'],
                             news['url']))
    total_time = time.time() - start_time
    print(f"Done in {total_time} sec.")


if __name__ == '__main__':
    main()
