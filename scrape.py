import re, shutil
from glob import glob
from pathlib import Path
from collections.abc import Iterable
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm # (if using normal .py files)
# from tqdm.notebook import tqdm # (if using Jupyter notebook)

# with open('proxies_list.txt') as file:
#   proxies_list = [line.rstrip() for line in file]

# proxies = {
#   'http': map(proxies_list),
#   'https': proxies_list
# }

def scrape(url: str) -> bs:
  try:
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs(r.text, 'html.parser')
  except Exception as e:
    print(e)
  
  return soup

def get_links_from_page(page: bs) -> list[str]:
  content_div = page.find('div', class_='entry-content')
  a_tags = content_div.find_all('a', href=True)
  links: list[str] = [a.get('href') for a in a_tags]
  return links

def flatten(xs):
  for x in xs:
    if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
      yield from flatten(x)
    else:
      yield x

def scrape_cmm_main_page(cmm_link: str) -> list[str]:
  # For Volume 10, Volume 11 & Volume 12 Prologue
  cmm_page = scrape(cmm_link)
  cmm_links = get_links_from_page(cmm_page)
  cmm_links = list(filter(lambda x: x.find('crimsonmagic.me') != -1, cmm_links))
  return cmm_links

def scrape_main_page():
  print('Scraping main page...')
  page = scrape('https://cgtranslations.me/konosuba/')
  links = get_links_from_page(page)

  # For Volume 10, Volume 11 & Volume 12 Prologue
  cmm_link = 'https://crimsonmagic.me/konosuba/volumes-10-plus/'
  # Remove duplicate Volume 12 prologue
  cmm_index = links.index(cmm_link)
  del links[cmm_index]
  # Insert the crimsonmagic links into links list
  cmm_links = scrape_cmm_main_page(cmm_link)
  links[cmm_index] = cmm_links
  links = flatten(links)

  #NOTE: TEMPORARILY SELECTING MAIN VOLUMES ONLY
  post_re = re.compile(r"cgtranslations.me\/(?:\d{4}\/\d{2}\/\d{2}\/|\?p=\d+)|crimsonmagic.me")
  links = list(filter(lambda x: post_re.search(x), links))

  return links

def scrape_post(link: str):
  metadata_re = re.compile(r"^(?:TL|Edit(?:ing|ors?)|Translat(?:or|ion)|<TL Note):", flags=re.IGNORECASE)
  sub_title_re = re.compile(r"^(?:TL|Edit(?:ing|ors?)|Translat(?:or|ion)|(?:Pro|Epi)logue|Chapter)", flags=re.IGNORECASE)

  print(f'Scraping {link}...')
  
  page = scrape(link)

  title = page.find(re.compile('h[12]'), class_='entry-title').get_text()
  content_div = page.find('div', class_='entry-content')

  sub_title_tag = content_div.find(['h1', 'h2'])
  if sub_title_tag is None:
    sub_title_tag = content_div.find('p', string=sub_title_re)
  if sub_title_tag is None:
    sub_title_tag = content_div.find('p')

  contents = list(sub_title_tag.find_next_siblings('p'))
  for tag in contents:
    try:
      tag.a.decompose()
    except:
      pass

  texts = [tag.get_text(strip=True) for tag in contents]
  texts = filter(None, texts) # Remove blanks
  texts = filter(lambda x: not metadata_re.match(x), texts)
  text = '\n'.join(list(texts))

  return (title, text)

def main():
  links = scrape_main_page()
  
  # Create data folder
  Path('./data').mkdir(parents=True, exist_ok=True)

  for index, link in enumerate(tqdm(links)):
    id = str(index).rjust(3, '0')
    
    if glob(f'./data/{id}*'):
      continue # skip already downloaded

    title, text = scrape_post(link)

    if len(text) <= 300:
      text = '' # Skip because it's probably manga

    text = f"Source: {link}\n{text}" # Include source link in file
    safe_title = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "_", title)

    with open(f"./data/{id} {safe_title}.txt", 'w') as file:
      file.write(text)
  
  with open('konosuba.txt','wb') as wfd:
    for f in glob('./data/[0-9][0-9][0-9]*'):
      with open(f,'rb') as fd:
        shutil.copyfileobj(fd, wfd)

if __name__ == "__main__":
  main()
