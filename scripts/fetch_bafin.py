import sys
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://portal.mvp.bafin.de/database/InstInfo/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

print("Page title:", soup.title.string if soup.title else "No title")

for form in soup.find_all('form'):
    print('Form action:', form.get('action'), 'method:', form.get('method'))
    for inp in form.find_all(['input', 'select']):
        name = inp.get('name')
        itype = inp.get('type')
        if inp.name == 'select':
            options = [(o.get('value'), o.text.strip()) for o in inp.find_all('option')]
            print(f"  SELECT {name}: {options[:10]}")
        else:
            val = inp.get('value')
            print(f"  INPUT {name} ({itype}) = {val}")
