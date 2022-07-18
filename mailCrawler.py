import re
import requests
import time
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

file = input('File address: ')

df = pd.read_csv(file)
urls = df['websites'].tolist()

urls = [x for x in urls if str(x) != 'nan']

for i in range(len(urls)):
    urls[i] = "https://" + urls[i]

emails = set()

print('Scraping started...')
    
for i in range(len(urls)):

    original_url = urls[i]

    unscraped = deque([original_url])

    scraped = set()

    while len(unscraped):
        url = unscraped.popleft()  
        scraped.add(url)

        parts = urlsplit(url)

        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
          path = url[:url.rfind('/')+1]
        else:
          path = url

        print("Crawling URL... %s" % url)
        
        try:
            response = requests.get(url, timeout = 20)
        except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
        emails.update(new_emails)
        
        soup = BeautifulSoup(response.text, 'lxml')

        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            
            else:
                link = ''

            if link.startswith('/'):
                link = base_url + link

            elif not link.startswith('http'):
                link = path + link
                
        if not link.endswith(".gz" ):
            if not link in unscraped and not link in scraped:
                if not link[-1] == link[-2]:
                    try:
                        if not unscraped[-1] in link:
                            unscraped.append(link)
                    except(IndexError):
                        pass
                    
        print('E-mail addresses found: ' + str(new_emails))
emails = list(emails)

print('Scraping is done. Saving as XLSX.')

for i in range(len(emails)):
    indexNo = df.index[df['websites'] == emails[i].split('@')[1]].tolist()
    
    if not (bool(indexNo)):
        indexNo = df.index[df['websites'] == (emails[i].split('@')[1] + '.tr')].tolist()
        emails[i] = emails[i] + '.tr'

    df['emails'][indexNo] = emails[i]
    
df.to_excel('email_addresses.xlsx')

print('File is saved.')
