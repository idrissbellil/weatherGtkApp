import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, GObject
from gi.repository.GdkPixbuf import Pixbuf
from io import BytesIO
from time import time, timezone, strftime, localtime
import requests
from glob import glob
import json
import iface
from copy import deepcopy
from utils import *

class Handler:
    def onDestroy(self, *args):
        try:
            print('SAVING THE ICONS')
            for key in iface.icons.keys():
                iface.icons[key].savev('icons/{}.png'.format(key), 'png', [], [])
        except Exception as e:
            print(e)
            pass
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

    def time_activated(self, view, child):
        elem = child.data

        # Load element results and set it in the interface
        city_field = child.city +  ': ' + str(elem['main']['temp']) + '°C\n' +\
                str(elem['wind']['speed']) + ' km/h'
        iface.city.set_label(city_field)
        
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

        iface.weather_icon.set_from_pixbuf(child.img.get_pixbuf())
        iface.win.show_all()


    def activated(self, view, data):
        # set research text the one selected
        search_query = data.get_child().get_text()
        iface.search_entry.set_text(search_query)

        # search the query and show the results
        GLib.idle_add(sync_updateui, search_query)

        # clean up for the next request
        self.delete_search_rows()
        iface.win.show_all()

    def update_ui(self, data, city, tm=None):
        if data is None:
          return

        if tm is None:
            curr_time = time() - timezone
            tm = int((curr_time // (3*3600)) * (3*3600))
        found = False

        if str(tm) not in data.keys():
          key = list(data.keys())[0]
          elem = data[key]
        else :
          elem = data[str(tm)]

        # Load element results and set it in the interface
        city_field = city +  ': ' + str(elem['main']['temp']) + '°C\n' +\
                str(elem['wind']['speed']) + ' km/h'
        iface.city.set_label(city_field)
        
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

        GLib.idle_add(sync_right_panel, data, city)

        iface.win.show_all()


    def save_query(self, data):
        pass
    
    def changed(self, arg):
        self.delete_search_rows(keep_right=True)
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

    def delete_search_rows(self, keep_right=False):
        lbox = iface.list_box
        widbox = iface.container
        for row in lbox.get_children():
            lbox.remove(row)
        if not keep_right:
            for row in widbox.get_children():
                widbox.remove(row)

def sync_right_panel(data, city):
    for dt in data.keys():
        if dt != 'updated':
            iface.container.add(WeatherWidget(data[dt], dt, city))
            iface.win.show_all()

def sync_updateui(city):
# This is meant to be used inside a thread
  data, city = sync_response(city)
  Handler().update_ui(data, city)
  
class WeatherWidget(Gtk.ListBoxRow):
    def __init__(self, data, tm, city):
        super(Gtk.ListBoxRow, self).__init__()

        # self some data needed later on
        self.tm = tm
        self.data = data
        self.city = city

        box = Gtk.Box()
        box.set_orientation(1)
        self.add(box)

        converted_time = int(tm) + timezone 
        formatted_time = strftime('%A %H:%M',localtime(int(converted_time)))
        curr_time = Gtk.Label(label=formatted_time)
        box.pack_start(curr_time, True, True, 0)

        wid_box = Gtk.Box()
        wid_box.set_orientation(0)
        box.pack_start(wid_box, True, True, 0)

        T = str(data['main']['temp']) + '°C'
        temp = Gtk.Label(label=T)
        wid_box.pack_start(temp, True, True, 0)

        img = Gtk.Image()
        wid_box.pack_start(img, True, True, 0)

        if  data['weather'][0]['icon'] in iface.icons.keys() :
            img.set_from_pixbuf(iface.icons[data['weather'][0]['icon']])
        else :
            # get the icon and show it
            url = 'http://openweathermap.org/img/w/{}.png'.format(
                      data['weather'][0]['icon'])

            response = requests.get(url)
            input_stream = Gio.MemoryInputStream.new_from_data(response.content, None) 
            pixbuf = Pixbuf.new_from_stream(input_stream, None) 
            iface.icons[data['weather'][0]['icon']] = pixbuf
            img.set_from_pixbuf(pixbuf)
        self.img = img

        iface.win.show_all()
        
def main():
    # attach the signals
    iface.builder.connect_signals(Handler())

    # get references and init the most used classes
    iface.search_bar.set_search_mode(False)
    iface.search_bar.connect_entry(iface.search_entry)

    # provide one city as an example
    GLib.idle_add(sync_updateui, 'tlemcen')

    try:
        names = glob('icons/*.png')
        for name in names:
            pixbuf = Pixbuf.new_from_file(name)
            key = name.split('/')[1].split('.')[0]
            iface.icons[key] = pixbuf
    except:
        pass

    iface.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    iface.stack.set_transition_duration(1000)
    
    fig_container = Gtk.Box()
    iface.stack.add_titled(fig_container, "fig_container", "Statistics")

    # Show and run
    iface.win.show_all()
    Gtk.main()

if __name__=='__main__':
    main()
