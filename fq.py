import re, sys

import requests
from pyquery import PyQuery as pq
from loguru import logger

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
PATTERN = re.compile(r'''function ajaxGetContent\(chapid\) \{ \$\.get\(\"\./_getcontent\.php\?id=\"\+chapid\+\"&v=(.*?)\"''')

def main():
    doc = pq(SESSION.get('https://fqbook.cc/read-312559.html').text)
    for script in doc('script').items():
        if 'function ajaxGetContent' in script.text():
            text = script.text()
    if not text:
        logger.error('failed')
        sys.exit()
    logger.info(text)
    token = PATTERN.search(text).group(1)
    url = 'https://fqbook.cc/_getcontent.php?id=312559&v=' + token
    print(SESSION.get(url).text)

if __name__ == '__main__':
    main()