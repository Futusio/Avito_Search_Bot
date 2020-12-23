from bs4 import BeautifulSoup
import requests
import csv
import logging
from logging import config
from conf import logger_config
import json
from time import time

IMAGE = f'https://klike.net/uploads/posts/2020-04/1587631210_4.jpg'
BLANK = ('Ошибка', 'Цена не указана', IMAGE)


logging.config.dictConfig(logger_config)
logger = logging.getLogger('web')

def get_items(url: str):
    """ The function scratchs data request
    and return main data """
    # Log string    
    logger.info(f'Get items from URL: \'{url}\'')
    # Variables
    r = get_html(url)
    if r == 404:
        return (0, None)
    soup = BeautifulSoup(r, 'lxml')
    # Actions 
    items = soup.find('div', class_='snippet-list').find_all('div', class_='snippet-horizontal') # Items list 
    count = int(soup.find(attrs={'data-marker':'page-title/count'}).text.replace(' ', '')) # Count of the items
    result = list(map(lambda x: get_items_data(x), items)) # Some do
    # Result
    return (count, result)


def get_items_data(soup: BeautifulSoup):
    """ The function scratch some data 
    of each passed item and returns 
    a dict with the data """
    try:
        name = soup.find('div', class_="item_table-wrapper").find('div', class_='description').h3.text[2:-2]
        url = 'https://avito.ru' + soup.find('a', class_='snippet-link').get('href')
    except Exception as e: # If exception is here 
        ID = int(time()) # File name
        logger.critical('New bug was found. Error is: {}\n\t\tSoup was written into \'{}.json\''.format(e, ID))
        with open('bugs\\{}.json'.format(ID), 'a', encoding='utf-8') as file: # Then write soup 
            file.write(json.dumps(str(soup), ensure_ascii=False)) # Into new json file
        return dict(zip(('name', 'price','img'), BLANK)) # And return blank 
    # The code below may raise exceptions   
    try: # The exception will raised if item has no image
        img = soup.find('img', class_='large-picture-img').get('srcset').split()[0]
    except:  # Then upload a blank image
        img = IMAGE
    try: # The exception will raised if item has no price
        price = soup.find(attrs={'data-marker':'item-price'}).text
    except: # Then price will equal text below
        price = "Цена не указана"
    return {'name': name,
            'price': price.strip(),
            'img': img, 
            'url': url
            }


def get_item_data(url: str):
    """ The function gets url string 
    and returns tuple of data of the item """
    # Log string 
    logger.info(f'Get data from item on URL: \'{url}\'')
    # Variables
    soup = BeautifulSoup(get_html(url), 'lxml')
    text = soup.find('div', class_='item-description').text # A description text
    gallery = soup.find_all('div', class_='gallery-extended-img-frame js-gallery-extended-img-frame') # All images 
    imgs = []
    for i, img in enumerate(gallery): # Gallery may be an empty
        if i == 20: break # Telegram supports only tweny medias 
        imgs.append(img.get('data-url'))
    # If imgs list is an empty - below image will be sent
    res = f'https://klike.net/uploads/posts/2020-04/1587631210_4.jpg'
    return (text, imgs) if len(imgs) != 0 else (text, [res,])


def get_html(url: str):
    r = requests.get(url)
    if r.ok: 
        return r.text
    else: 
        logger.warning(f'The request on url: {url}\n\t\treturned {r.status_code} code')
        return r.status_code