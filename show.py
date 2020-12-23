import parsing
import logging 
from models import *

class Data(object):
    def __init__(self, request, user):
        self.pattern = "https://www.avito.ru/{}?p={}&q={}" # Pattern 
        self.city = user.region
        self.request = request.replace(' ', '+')
        self.page = 1 # Number of page
        self.current = 0 # Current item ID 
        # Will fill later
        self.count, self.items = parsing.get_items(self.get_url())
        self.above = None # An ID of 
        self.item = None # Later



    def get_current_number(self): # Returns item current number
        return (self.page*50 - 50) + self.current + 1

    def get_item(self, attr = None): # Returns current item
        if attr is None:
            return self.items[self.current]
        else:
            try:
                return self.items[self.current][attr]
            except: # Exception was raised if obj fill with blank 
                return None

    def get_item_data(self):
        self.item = Item(self.get_item('name'), *parsing.get_item_data(self.get_item('url')))

    def get_url(self): # Return current URL 
        return self.pattern.format(self.city, self.page, self.request)

    def next_item(self):
        self.current += 1
        if self.get_current_number() == self.count: # Is the last item?
            return 'last'
        if self.current == 50:
            self.page += 1
            self.current = 0
            self.count, self.items = parsing.get_items(self.get_url())
        return 'ok'

    def prev_item(self):
        self.current -= 1
        if self.get_current_number()-1 == 0:
            return 'first'
        return 'ok'

    def __repr__(self):
        return f'<Request is {self.request}, It has {self.count} items'


class Item():
    def __init__(self, name, caption, images):
        self.name = name
        self.caption = caption if len(caption) < 1024 else caption[:990] + '...\n\n\tПродолжение на avito.ru'
        self.images = images
        self.current = 0

    def get_img(self):
        return self.images[self.current]

    def next_img(self):
        self.current += 1
        if self.current == len(self.images)-1: # If a current item is the last
            return ('last', self.images[self.current])
        else:
            return ('ok', self.images[self.current])

    def prev_img(self):
        self.current -= 1
        if self.current == 0:  # If a current item is the first 
            return ('first', self.images[self.current])
        else:
            return ('ok', self.images[self.current])

    def __repr__(self):
        return f'<Item: {self.name}'