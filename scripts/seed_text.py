import json
import re

import requests
from bs4 import BeautifulSoup


r = requests.get('https://terebess.hu/english/tao/mitchell.html')
soup = BeautifulSoup(r.text, 'html.parser')

output = {}

for tag in soup.find_all('p', align='left'):
    font_tags = tag.find_all('font')
    if font_tags and len(font_tags) < 3:
        for font_tag in font_tags:
            chapter_text = font_tag.get_text()
            if chapter_text:
                chapter_no = re.match(r'\d+', chapter_text)[0]
                output[chapter_no] = '\r\n'.join(
                    map(str.strip, chapter_text.split('\r\n')))

with open('daily_tao/tao.json', 'w') as out_file:
    json.dump(output, out_file, indent=4, sort_keys=True)
