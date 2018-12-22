from pathlib import Path
import json
import requests
import json
import iface
from copy import deepcopy
from time import time, timezone

class CustomTrie:

    def __init__(self, word_list=[]):
        self.trie = {}
        self.add_list_of_words(word_list)

    def add_word(self, word, n=3):
        """Add a single word to the trie
        """
        if word[:n] not in self.trie.keys() :
            self.trie[word[:n]] = {}
    
        it = self.trie[word[:n]]
        for char in word[n:]:
            if char not in it.keys():
                it[char] = {}
            it = it[char]
    
    def add_list_of_words(self, word_list, n=3):
        """Add a list of words to the trie
        """
        for word in word_list:
            self.add_word(word, n=n)
    
    def find_substring(self, sub):
        """Find a substring in a trie
        """
        it = self.trie
        if sub[:3] in it.keys():
            it = it[sub[:3]]
        else :
            return {}
        for char in sub[3:]:
            if char in it.keys():
                it = it[char]
            else :
                break
        return deepcopy(it)
    
    def get_suggestions(self, substring):
        """Get a pointer to the top of a trie that
        matches the given sub-string suggestions
        """
        it_suggestions = self.find_substring(substring)
        
        # This to take only 3 top suggestions not to overload user's
        # ui with city suggestions
        suggestions = self.tolist(it_suggestions)[:3]
        return suggestions
    
    
    def tolist(self, it=None):
        """
        Converts a trie to a list of words, it uses root trie by default
        Dictionary reduction till having a flat dictionary
        """

        if it is None:
            it = deepcopy(self.trie)
        
        theres_change = True
        while theres_change :
            theres_change = False
            for char in list(it.keys()):
                char_changed = False
                for n_char in list(it[char].keys()):
                    it[char + n_char] = it[char].pop(n_char)
                    char_changed = True
                    theres_change = True
                if char_changed:
                    it.pop(char)
        return list(it.keys())

def sync_response(city):
    """
    Uses the Open Weather Map API to provide a json results of the weather API
    """
    user_key = 'be984db413b4ecae2062c6801b3240dd'
    url = "http://api.openweathermap.org/data/2.5/forecast?q={}&APPID={}&units=metric"\
              .format(city, user_key)

    # Test First if we have a recent record of this entry in our log
    try :
        with open('log/dump.log', 'r') as f:
            store = json.load(f)

    except Exception as e:
        store = {}
        log = Path('log')
        if not log.exists():
            log.mkdir()
            
    else:
        if city in store.keys() :
          curr_time = time() - timezone
          time_slot = int((curr_time // (3*3600)) * (3*3600))
          # the openweather api suggests sync every 3 hours
          if ((time() - store[city]['updated']) <= 3*3600) and\
                (str(time_slot) in store[city].keys()):
            # execution finishes here if city, time updated found
            return store[city], city
            
    # Sync if necessary
    print('City not found so loading the data from the internet')
    response = requests.get(url)
    data = response.json()
    
    if data['cod'] == '200':
      city = data['city']['name'].lower()
      if city not in store.keys():
        store[city] = {}
      for elem in data['list']:
        store[city][str(elem['dt'])] = elem
    
      store[city]['updated'] = time()
      with open('log/dump.log', 'w') as f:
        json.dump(store, f)

      return store[city], city
      
    else:
      print(data)
      return None, None

def json2citylist(fn):
    """Parse the json file looking only for city names"""
    with open(fn, 'r') as f:
        data = json.load(f)

    list_cities = [place['name'].lower() for place in data]

    return list_cities

