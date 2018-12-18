import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf
from threading import Thread
from io import BytesIO
from time import time, timezone
import requests
import json
import iface
from copy import deepcopy
from utils import *

class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()
    
    def add(self, arg, add):
        pass

    def check_resize(self, arg):
        pass

    def remove(self, view, data):
        pass

    def set_focus_child(self, arg, child):
        pass

    def next_match(self, arg):
        pass
    
    def previous_match(self, arg):
        pass

    def selected(self, view, data):
        pass

    def activated(self, view, data):
        # set research text the one selected
        search_query = data.get_child().get_text()
        iface.search_entry.set_text(search_query)

        # search the query and show the results
        t = Thread(target=sync_updateui, args=[search_query])
        t.start()

        # clean up for the next request
        self.delete_search_rows()
        iface.win.show_all()

    def update_ui(self, data, city):
        if data is None:
          return
        curr_time = time() - timezone
        tm = int((curr_time // (3*3600)) * (3*3600))
        found = False

        if str(tm) not in data.keys():
          return
        elem = data[str(tm)]

        # Load element results and set it in the interface
        city += ': ' + str(elem['main']['temp']) + '°C\n' +\
                str(elem['wind']['speed']) + ' km/h'
        iface.city.set_label(city)
        
        # set the pressure
        iface.pressure.set_label('Pressure: ' + str(elem['main']['pressure']))
        # set the Humidity
        iface.humidity.set_label('Humidity: ' + str(elem['main']['humidity']))
        # set temperatures max and min
        iface.minmax.set_label('{} ~ {} °C'.format(elem['main']['temp_min'],
            elem['main']['temp_max']))
            
        # set the comment and the description
        iface.comment.set_label(elem['weather'][0]['main'] + '\n' + 
                elem['weather'][0]['description'])
                
        # get the icon and show it
        url = 'http://openweathermap.org/img/w/{}.png'.format(
                  elem['weather'][0]['icon'])
        response = requests.get(url)
        input_stream = Gio.MemoryInputStream.new_from_data(response.content, None) 
        pixbuf = Pixbuf.new_from_stream(input_stream, None) 
        iface.weather_icon.set_from_pixbuf(pixbuf)
        
        # turn searchBar search mode to off
        iface.search_bar.set_search_mode(False)


    def save_query(self, data):
        pass
    
    def changed(self, arg):
        self.delete_search_rows()
        iface.search_bar.set_search_mode(True)

        search_str = iface.search_entry.get_text().lower()
        if len(search_str)>=3 :
            suggestions = get_suggestions(search_str, iface.trie)
            self.add_row(search_str)
            for suggestion in suggestions:
                self.add_row(search_str + suggestion)

    def add_row(self, name):
        row = Gtk.ListBoxRow()
        row.add(Gtk.Label(label=name))
        iface.list_box.add(row)
        iface.win.show_all()
    
    def stop(self, arg):
        iface.search_bar.set_search_mode(False)
        self.delete_search_rows()

    def delete_search_rows(self):
        lbox = iface.list_box
        for row in lbox.get_children():
            lbox.remove(row)
def main():
    # attach the signals
    iface.builder.connect_signals(Handler())

    # get references and init the most used classes
    iface.search_bar.set_search_mode(False)
    iface.search_bar.connect_entry(iface.search_entry)

    # provide one city as an example
    t = Thread(target=sync_updateui, args=['tlemcen'])
    t.start()

    # Show and run
    iface.win.show_all()
    iface.win.connect("destroy", Gtk.main_quit)
    Gtk.main()
    t.join()

def sync_updateui(city):
# This is meant to be used inside a thread
  data, city = sync_response(city)
  Handler().update_ui(data, city)
  
if __name__=='__main__':
    main()
