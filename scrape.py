import re, shutil
from glob import glob
from pathlib import Path
from collections.abc import Iterable
from requests_cache import CachedSession
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

session = CachedSession(expire_after=60 * 60 * 24) # Cache for 1 day

def scrape(url: str):
  """Download and parse a webpage using BeautifulSoup

  Args:
      url (str): URL of the webpage.

  Returns:
      BeautifulSoup: The page.
  """
  try:
    r = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs(r.text, 'html.parser')
    return soup
  except Exception as e:
    print(e)

def get_links_from_page(page: bs) -> list[str]:
  """Get all the anchor tags from a page's content

  Args:
      page (BeautifulSoup): The page.

  Returns:
      list[str]: List of URLs.
  """
  content_div = page.find('div', class_='entry-content')
  a_tags = content_div.find_all('a', href=True)
  links: list[str] = [a.get('href') for a in a_tags]
  return links

def flatten(xs):
  """https://stackoverflow.com/a/2158532/16259910"""
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
  # Download the page
  page = scrape(link)

  title = page.find(re.compile('h[12]'), class_='entry-title').get_text()
  content_div = page.find('div', class_='entry-content')

  # Filters
  sub_title_re = re.compile(
    r"^(?:TL|Edit(?:ing|ors?)|Translat(?:or|ion)|(?:Pro|Epi)logue|Chapter)",
    flags=re.IGNORECASE
  )
  sub_title_tag = content_div.find(['h1', 'h2'])
  if link.find('crimsonmagic.me') != -1:
    # Apply for crimsonmagic.me only
    strong_tag = content_div.select_one('hr~p>strong')
    if strong_tag is None:
      strong_tag = content_div.select_one('hr~p>b')
    if strong_tag is not None:
      sub_title_tag = strong_tag.parent
  if sub_title_tag is None:
    sub_title_tag = content_div.find('p', string=sub_title_re)
  if sub_title_tag is None:
    # Just use first p tag as subtitle
    sub_title_tag = content_div.find('p')
    # print('USING FIRST P TAG: ' + link)

  afterwords_re = re.compile('afterword', flags=re.IGNORECASE)
  afterwords_tag = content_div.find(['h1', 'h2'], string=afterwords_re)
  if afterwords_tag is not None:
    # Remove stuff after that
    try:
      for tag in afterwords_tag.find_next_siblings('p'):
        tag.decompose()
      afterwords_tag.decompose()
      # print('AFTERWORDS: ' + link)
    except:
      pass
  
  notes_re_list = [
    '^Notes about this chapter:',
    '^Extra Note(?:s|\(s\) ):',
  ]
  notes_re = re.compile('|'.join(notes_re_list), flags=re.IGNORECASE)
  notes_tag = content_div.find('p', string=notes_re)
  if notes_tag is not None:
    # Remove notes after that
    try:
      for tag in notes_tag.find_next_siblings('p'):
        tag.decompose()
      notes_tag.decompose()
      # print('NOTES: ' + link)
    except:
      pass
  
  if link.find('crimsonmagic.me') != -1:
    # Apply for crimsonmagic.me only
    quiz_tag = content_div.select_one('h1>strong')
    try:
      if quiz_tag.get_text() == 'QUIZ TIME:':
    # Remove quiz after that
        for tag in quiz_tag.parent.find_next_siblings('p'):
          tag.decompose()
        quiz_tag.decompose()
        # print('QUIZ: ' + link)
    except:
      pass

  # Get text content from all p
  contents = list(sub_title_tag.find_next_siblings('p'))
  for tag in contents:
    # Remove links inside p
    try:
      for a in tag.find_all('a'):
        a.decompose()
    except:
      pass

  # More filters
  texts = map(lambda tag: tag.get_text(strip=True), contents) # Get texts
  texts = filter(None, texts) # Remove blanks
  
  # Remove TL metadata
  # this crazy ass regex list :skull:
  metadata_re_list = map(lambda x: '^'+x, [
    'TL',
    'Edit(?:ing|ors?)',
    'Translat(?:or|ion):',
    '[<[{]TL Note',
    'Afterdrawing',
    'Illustrator’s afterart',
    r'Pa[rt]t \d+?',
    r'Chapter \d+?',
    'Preview:',
    'Next volume preview',
    'Source @ ?CGtranslations.me',
    'Updated:',
    r'Translated by yuNS @ crimsonmagic \. me',
    r'END OF CHAPTER \d+?',
    r'Share this:LikeLoading\.\.\.Related',
    'Vol 12 Gamers exclusive short story',
    r'\[',
    '<Incidentally',
    '<See:',
    '<Important Note:',
    '<Thanks to Kasen',
    '<Press F for Kazuma',
    'Because the illustrators failed to include any pictures of Lord Zereshrute',
    'Because they once again failed to include any pictures of Duke’s face',
    'Well, this is the last short story that I have for volume 13',
    'Anyway, it’s been a fun time. I hope you’ve enjoyed volume 13',
    '(Thanks to Ulti and Kasen for providing these)',
    'Volume 15 will be running all throughout the month of January',
    'Coloured illustrations: Kasen',
    '(Thanks to Ulti and Kasen for providing these)',
    'From the Digital Special Edition',
  ])
  metadata_re = re.compile('|'.join(metadata_re_list), flags=re.IGNORECASE)
  texts = filter(lambda x: not bool(metadata_re.match(x)), texts) 

  # Remove chapter nav from crimsonmagic.me
  chap_nav_re = re.compile(r'^\|(?: Next Chapt?er)?')
  texts = filter(lambda x: not bool(chap_nav_re.match(x)), texts)

  # Remove trailing period from "…."
  texts = map(lambda x: re.compile(r'…\.+').sub('…', x), texts)

  # Remove (TL Note: xxxx)
  texts = map(lambda x: re.compile(r'(TL Note:.+?)', flags=re.IGNORECASE).sub('', x), texts)

  text = '\n'.join(list(texts))
  
  # Special case of afterword needed to be removed lmao
  if title.find('Volume 10, Epilogue + Side Stories') != -1:
    text = re.sub('Author’s Afterword[\s\S]+Akatsuki Natsume\n', '', text)

  return (title, text)

def main():
  links = scrape_main_page()
  
  # Create data folder
  Path('./data').mkdir(parents=True, exist_ok=True)

  print(f"Scraping all {len(links)} posts...")
  for index, link in enumerate(tqdm(links)):
    id = str(index).rjust(3, '0')
    
    # if glob(f'./data/{id}*'):
    #   continue # skip already downloaded

    # print(f'Scraping {id} {link}...')
    title, text = scrape_post(link)

    if text.count('\n') <= 10:
      text = '' # Skip because it's probably manga

    # Include source link in file
    text = f"Source: {link}\n{text}".rstrip()
    # Clean the title for a safe filename
    safe_title = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', title)

    # Write to ./data folder
    with open(f"./data/{id} {safe_title}.txt", 'w') as file:
      file.write(text)
      file.write('\n')
  
  print('Combining all posts to konosuba.txt...')
  with open('konosuba.txt','wb') as wfd:
    files = glob('./data/[0-9][0-9][0-9]*')
    file_re = re.compile(r"(\d{3}) ")
    files.sort(key=lambda x: int(file_re.search(x)[1]))
    
    for f in files:
      with open(f,'rb') as fd:
        fd.readline() # Skip first line (source link)
        shutil.copyfileobj(fd, wfd)
  
  print('Extracting dialogues from konosuba.txt to konosuba-dialogue.txt...')
  with open('konosuba.txt', 'r') as konosuba:
    lines = konosuba.readlines()

    dialogue_re = re.compile(r'“(.+?)”')
    def get_dialogue(line: str):
      matches = dialogue_re.findall(line)
      if len(matches) > 0:
        return matches
      return ''
    
    # Remove awkward ......
    silence_re = re.compile(r'^[… ]+?$')
    def filter_silence(line: str):
      return not bool(silence_re.match(line))

    dialogues = flatten(map(get_dialogue, lines))
    dialogues = filter(filter_silence, dialogues)
    dialogues = filter(None, dialogues) # Filter blanks
    dialogues_text = '\n'.join(dialogues)
  
  with open('konosuba-dialogue.txt', 'w') as konosuba_dialogue:
    konosuba_dialogue.write(dialogues_text)
  
  print("Done.")
  print("Check out konosuba.txt and konosuba-dialogue.txt for all of your KonoSuba needs :p")

if __name__ == '__main__':
  main()
