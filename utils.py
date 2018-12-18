# This should certainly be redesigned as OOP

import json
import requests
import json
import iface
from copy import deepcopy

def create_dict(word, dic={}, n=3):
    """Create a trie with dictionaries as nodes given one word
    and an optional initial dictionary
    """
    if word[:n] not in dic.keys() :
        dic[word[:n]] = {}

    it = dic[word[:n]]
    for char in word[n:]:
        if char not in it.keys():
            it[char] = {}
        it = it[char]
    return dic

def create_trie(word_list, dic={}, n=3):
    """Create a trie of dictionary nodes given a list of words
    """
    for word in word_list:
        create_dict(word, dic, n=n)
    return dic

def find_substr(sub, trie):
    """Find a substring in a trie
    """
    it = trie
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

def trie_to_list(it):
    """
    Converts a trie to a list of words
    Dictionary reduction till having a flat dictionary
    """
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
    with open('log/dump.log', 'r') as f:
        dump = json.dump(f)

    # Symc if necessary
    response = requests.get(url)
    return response.json()

def json2citylist(fn):
    """Parse the json file looking only for city names"""
    with open(fn, 'r') as f:
        data = json.load(f)

    list_cities = [place['name'].lower() for place in data]

    return list_cities

def get_suggestions(string, trie):
    it_suggestions = find_substr(string, trie)
    
    # This to take only 3 top suggestions to overload user's
    # computer with city suggestions
    suggestions = trie_to_list(it_suggestions)[:3]
    return suggestions

