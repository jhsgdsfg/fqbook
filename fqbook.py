import re
import sys
import time
from urllib.parse import urljoin

import requests
from pyquery import PyQuery as pq
from loguru import logger

BASE_URL = 'https://fqbook.cc'
URL = 'https://fqbook.cc/read-318596.html'
TXT = open('txt/纯爱后宫港区_UTF8.txt', 'w', encoding='utf-8')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
ID_PATTERN = re.compile(r'read-(.*?).html')
TOKEN_PATTERN = re.compile(r'''function ajaxGetContent\(chapid\) \{ \$\.get\(\"\./_getcontent\.php\?id=\"\+chapid\+\"&v=(.*?)\"''')

def scrape_page(url):
    return SESSION.get(url).text

def scrape_index(url):
    return scrape_page(url)

def scrape_detail(url):
    url = urljoin(BASE_URL, url)
    return scrape_page(url)

def scrape_content(token, id):
    url = f'{BASE_URL}/_getcontent.php?id={id}&v={token}'
    return scrape_page(url)

def parse_index(html):
    doc = pq(html)
    urls = [ a.attr('href') for a in doc('.section_list')('li')('a').items()]
    ids = [ re.search(ID_PATTERN, url).group(1) for url in urls ]
    return {'urls': urls, 'ids': ids}

def parse_detail(html):
    doc = pq(html)
    for script in doc('script').items():
        if 'function ajaxGetContent' in script.text():
            text = script.text()
    if not text:
        logger.error('failed')
        sys.exit()
    token = TOKEN_PATTERN.search(text).group(1)
    TXT.write(doc('.chapter_title').text())
    TXT.write('\n')
    return token

def parse_content(html):
    doc = pq(html)
    for p in doc('p').items():
        if p.children():
            p.children().remove()
        if not p.text():
            continue
        TXT.write(p.text())
        TXT.write('\n')

def main():
    index = scrape_index(URL)
    res = parse_index(index)
    logger.info('scraped index')
    for i in range(len(res['urls'])):
        detail = scrape_detail(res['urls'][i])
        token = parse_detail(detail)
        content = scrape_content(token, res['ids'][i])
        parse_content(content)
        logger.info(f'scraped detail {i + 1}/{len(res["urls"])}')
        time.sleep(0.5)


if __name__ == '__main__':
    try:
        main()
    finally:
        TXT.close()
        SESSION.close()