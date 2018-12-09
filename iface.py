import gi
from utils import *
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

builder = Gtk.Builder()

builder.add_from_file("xml/main.xml")

cities_list = json2citylist('city.list.json')

trie = create_trie(cities_list)

win = builder.get_object('main_window')

search_bar = builder.get_object('search_bar')

search_entry = builder.get_object('search_entry')

humidity = builder.get_object('humidity')

pressure = builder.get_object('pressure')

minmax = builder.get_object('minmax')

weather_icon = builder.get_object('weather_icon')

city = builder.get_object('city')

comment = builder.get_object('comment')

list_box = builder.get_object('list_box')