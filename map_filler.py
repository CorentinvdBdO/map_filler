#!/usr/bin/env python3

import sys
import csv
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gegl
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Babl
import random

# Presets
## Games
CK3 = "CK3"

## Modes
PROVINCES_CSV = "PROVINCES_CSV"  # A custom csv that needs to be parsed into the various files
DEFINITION = "DEFINITION"      # Directly editing the DEFINITION files (CK3)
# DEFINITION file is a headerless csv with the following columns: id;r;g;b;name[As many columns, can have spaces];x

# Variables
provinces_csv = "/home/user/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Crusader Kings III/game/map_data/definition.csv"

delimiter = ";"
NO_HEADERS = False
SKIP_FIRST_LINE = False


GAME = CK3            # Could be expanded to other paradox games
MODE = DEFINITION  # PROVINCES_CSV or DEFINITION

ID = "id"
R = "r"
G = "g"
B = "b"
NAME = "name"

csv_columns = [ID, R, G, B, NAME]

def color_to_string(r, g, b) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def string_to_color(color_string: str) -> tuple[int, int, int]:
    return tuple(int(color_string[i:i+2], 16) for i in (1, 3, 5))

def read_provinces_csv() -> dict[int, dict]:
    """
    Returns all provinces
    """
    if MODE == PROVINCES_CSV:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            return {int(row[ID]): row for row in csv_reader if row[ID] != ""}
        
    elif MODE == DEFINITION:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.reader(file, delimiter=";")
            lines = [row for row in csv_reader]
            if SKIP_FIRST_LINE:
                lines.pop(0)
            csv_dict = {}
            for line in lines:
                if line[0].strip() == "":
                    continue
                if line[0].strip().startswith("#"):
                    continue
                id = int(line[0])
                r = line[1]
                g = line[2]
                b = line[3]
                name = ' '.join(line[4:])
                name = name.split("#")[0] # Remove comments
                name = name.strip()
                if name.endswith("x"):
                    name = name[:-1]
                name = name.strip()
                csv_dict[id] = {"id": id, "r": r, "g": g, "b": b, "name": name}
            return csv_dict


def read_province(id: int) -> dict:
    """
    Return only the province with the given id
    """
    if MODE == PROVINCES_CSV:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            return next((row for row in csv_reader if int(row[ID]) == id), None)
    elif MODE == DEFINITION:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.reader(file, delimiter=";")
            lines = [row for row in csv_reader]
            if SKIP_FIRST_LINE:
                lines.pop(0)
            for line in lines:
                if line[0].strip() == "":
                    continue
                if line[0].strip().startswith("#"):
                    continue
                id = int(line[0])
                if id != id:
                    continue
                r = line[1]
                g = line[2]
                b = line[3]
                name = ' '.join(line[4:])
                name = name.split("#")[0] # Remove comments
                name = name.strip()
                if name.endswith("x"):
                    name = name[:-1]
                name = name.strip()
                return {"id": id, "r": r, "g": g, "b": b, "name": name}
            return None

def read_province_by_color(r, g, b) -> dict:
    r = str(r)
    g = str(g)
    b = str(b)
    if MODE == PROVINCES_CSV:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            for row in csv_reader:
                if row[R] == r and row[G] == g and row[B] == b:
                    return row
                
    elif MODE == DEFINITION:
        with open(provinces_csv, 'r') as file:
            csv_reader = csv.reader(file, delimiter=";")
            lines = [row for row in csv_reader]
            if SKIP_FIRST_LINE:
                lines.pop(0)
            for line in lines:
                if line[0].strip() == "":
                    continue
                if line[0].strip().startswith("#"):
                    continue
                id = int(line[0])
                row_r = line[1]
                if row_r != r:
                    continue
                row_g = line[2]
                if row_g != g:
                    continue
                row_b = line[3]
                if row_b != b:
                    continue
                name = ' '.join(line[4:])
                name = name.split("#")[0] # Remove comments
                name = name.strip()
                if name.endswith("x"):
                    name = name[:-1]
                name = name.strip()
                return {"id": id, "r": row_r, "g": row_g, "b": row_b, "name": name}
        
    return None

def build_color_set(provinces: dict[int, dict]) -> set[str]:
    color_set = set()
    for province in provinces.values():
        try:
            r = int(province[R])
            g = int(province[G])
            b = int(province[B])
            color_set.add(color_to_string(r, g, b))
        except ValueError:
            continue
    return color_set

def save_provinces_csv(provinces: dict[int, dict]):
    if MODE == PROVINCES_CSV:
        with open(provinces_csv, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=csv_columns, delimiter=delimiter)
            csv_writer.writeheader()
            for province in provinces.values():
                csv_writer.writerow(province)

    elif MODE == DEFINITION:
        with open(provinces_csv, 'w') as file:
            csv_writer = csv.writer(file, delimiter=";")
            for province in provinces.values():
                row = [province[ID], province[R], province[G], province[B], province[NAME], "x"]
                csv_writer.writerow(row)

def add_province(provinces: dict[int, dict], new_province: dict):
    provinces[new_province[ID]] = new_province
    save_provinces_csv(provinces)

def new_color(colors_set, max_tries=100):
    """
    Give a new random color not already in the list
    """
    for _ in range(max_tries):
        new_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        new_color_string = color_to_string(*new_color)
        if new_color_string not in colors_set:
            return new_color, new_color_string
    raise Exception("Failed to find a new color")

def get_color_ints(provinces, province_id):
    return int(provinces[province_id][R]), int(provinces[province_id][G]), int(provinces[province_id][B])

def get_color_string(provinces, province_id):
    r, g, b = get_color_ints(provinces, province_id)
    return color_to_string(r, g, b)

def get_province_id(provinces, color_string):
    for province_id, province in provinces.items():
        if get_color_string(province) == color_string:
            return province_id
    return None

def set_foreground_color(color_string):
    Gimp.context_set_foreground(Gegl.Color.new(color_string))

def get_foreground_color():
    color = Gimp.context_get_foreground()

    rgba = color.get_rgba_with_space(Babl.space("sRGB"))

    r = int(rgba[0] * 255)
    g = int(rgba[1] * 255)
    b = int(rgba[2] * 255)

    return r, g, b

class ProvicesPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        # Return list of all procedures this plugin provides
        return [
            "map-filler-select", 
            "map-filler-random", 
            "map-filler-add", 
            "map-filler-get-from-color", 
            "map-filler-add-from-color"
        ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        # Create different procedures based on name
        procedure = None
        
        if name == "map-filler-select":
            procedure = Gimp.ImageProcedure.new(self, name,
                                              Gimp.PDBProcType.PLUGIN,
                                              self.run_select, None)
            
            procedure.set_image_types("*")
            procedure.set_menu_label("Get Province Color")
            procedure.add_menu_path('<Image>/Provinces/')
            
        elif name == "map-filler-random":
            procedure = Gimp.ImageProcedure.new(self, name,
                                              Gimp.PDBProcType.PLUGIN,
                                              self.run_random, None)
            
            procedure.set_image_types("*")
            procedure.set_menu_label("Choose Random Color")
            procedure.add_menu_path('<Image>/Provinces/')
            
        elif name == "map-filler-add":
            procedure = Gimp.ImageProcedure.new(self, name,
                                              Gimp.PDBProcType.PLUGIN,
                                              self.run_add, None)
            
            procedure.set_image_types("*")
            procedure.set_menu_label("Create Province")
            procedure.add_menu_path('<Image>/Provinces/')

        elif name == "map-filler-get-from-color":
            procedure = Gimp.ImageProcedure.new(self, name,
                                              Gimp.PDBProcType.PLUGIN,
                                              self.run_get_from_color, None)
            
            procedure.set_image_types("*")
            procedure.set_menu_label("Get Province from Color")
            procedure.add_menu_path('<Image>/Provinces/')

        elif name == "map-filler-add-from-color":
            procedure = Gimp.ImageProcedure.new(self, name,
                                              Gimp.PDBProcType.PLUGIN,
                                              self.run_add_from_color, None)
            
            procedure.set_image_types("*")
            procedure.set_menu_label("Create Province from Color")
            procedure.add_menu_path('<Image>/Provinces/')

        if procedure:
            procedure.set_documentation(
                f"CK3 province plugin - {name}",
                f"CK3 province plugin - {name}",
                name)
            procedure.set_attribution("Kerbourgnec", "Kerbourgnec", "2025")

        return procedure

    def run_select(self, procedure, run_mode, image, drawables, config, run_data):
        GimpUi.init("map-filler")
        
        # Create the dialog
        dialog = GimpUi.Dialog(use_header_bar=True,
                              title="Province Selector",
                              role="map-filler")
        
        # Create a vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=12)
        dialog.get_content_area().add(vbox)
        
        # Add a search entry
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search provinces...")
        vbox.add(search_entry)
        
        # Create a scrolled window for the list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        vbox.pack_start(scrolled, True, True, 0)
        
        # Create ListStore to hold the data
        # Columns: province_id, display_text
        list_store = Gtk.ListStore(int, str)
        
        # Populate the list store
        provinces = read_provinces_csv()
        for province in provinces.values():
            display_text = f"{province[ID]} - {province[NAME]}"
            list_store.append([int(province[ID]), display_text])
        
        # Create a filter for the list store
        self.current_filter_text = ""
        tree_filter = list_store.filter_new()
        tree_filter.set_visible_func(self.filter_func)
        
        # Create TreeView with the filtered model
        tree_view = Gtk.TreeView(model=tree_filter)
        tree_view.set_headers_visible(False)
        
        # Add column to display text
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Province", renderer, text=1)
        tree_view.append_column(column)
        
        # Add TreeView to scrolled window
        scrolled.add(tree_view)
        
        # Store the current filter text
        self.current_filter_text = ""
        
        # Connect search entry to filter function
        def on_search_changed(entry):
            self.current_filter_text = entry.get_text().lower()
            tree_filter.refilter()
        
        search_entry.connect('search-changed', on_search_changed)
        
        # Add buttons
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)
        
        # Select first item by default
        selection = tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.select_path(Gtk.TreePath.new_first())
        
        # Show dialog and get response
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            model, tree_iter = selection.get_selected()
            if tree_iter is not None:
                # Convert filtered iter to original model iter
                child_iter = model.convert_iter_to_child_iter(tree_iter)
                province_id = list_store[child_iter][0]  # Get the province ID
                province = provinces[province_id]
                try: 
                    r = int(province[R])
                    g = int(province[G])
                    b = int(province[B])
                except ValueError:
                    new_rgb, new_color_str = new_color(colors)
                    r, g, b = new_rgb

                color_string = color_to_string(r, g, b)
                set_foreground_color(color_string)
                Gimp.message(f"Selected province: {list_store[child_iter][1]}")
        
        dialog.destroy()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def filter_func(self, model, iter, data):
        """Filter function for the tree model"""
        if self.current_filter_text == "":
            return True
        
        text = model[iter][1].lower()
        return self.current_filter_text in text

    def run_random(self, procedure, run_mode, image, drawables, config, run_data):
        provinces = read_provinces_csv()
        colors = build_color_set(provinces)
        
        # Get new random color not in set
        new_rgb, new_color_str = new_color(colors)
        
        # Set as foreground color
        set_foreground_color(new_color_str)
        
        Gimp.message(f"New random color: {new_color_str}")
        
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    
    def add_province_interface(self, procedure, new_rgb, new_color_str):
        provinces = read_provinces_csv()
        colors = build_color_set(provinces)

        # Initialize GimpUi
        GimpUi.init("map-filler")

        # Create the dialog
        dialog = GimpUi.Dialog(use_header_bar=True,
                              title="Add Province",
                              role="map-filler")

        # Create a vertical box for layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=6)
        dialog.get_content_area().add(vbox)

        # Add a label
        label = Gtk.Label(label="Enter province name:")
        vbox.add(label)

        # Add text entry
        entry = Gtk.Entry()
        entry.set_text("New Province")  # Default text
        entry.set_activates_default(True)  # Enter key triggers default button
        vbox.add(entry)

        # Add buttons
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        # Show dialog and get response
        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            name = entry.get_text()
            
            
            new_province = {
                ID: len(provinces) + 1,
                NAME: name,
                R: new_rgb[0],
                G: new_rgb[1],
                B: new_rgb[2]
            }
            
            add_province(provinces, new_province)
            set_foreground_color(new_color_str)
            Gimp.message(f"Added province: {name}")

        dialog.destroy()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def run_add(self, procedure, run_mode, image, drawables, config, run_data):
        provinces = read_provinces_csv()
        colors = build_color_set(provinces)
        new_rgb, new_color_str = new_color(colors)
        return self.add_province_interface(procedure, new_rgb, new_color_str)

    def run_get_from_color(self, procedure, run_mode, image, drawables, config, run_data):
        r, g, b = get_foreground_color()
        print(r, g, b)
        province = read_province_by_color(r, g, b)
        if province is None:
            Gimp.message("No province found")
        else:
            Gimp.message(f"Id: {province[ID]} - Name: {province[NAME]}")
        
        GimpUi.init("map-filler")

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def run_add_from_color(self, procedure, run_mode, image, drawables, config, run_data):
        r, g, b = get_foreground_color()
        new_rgb = (r, g, b)
        new_color_str = color_to_string(r, g, b)
        province = read_province_by_color(r, g, b)
        if province is not None:
            Gimp.message(f"Province already exists: Id: {province[ID]} - Name: {province[NAME]}")
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
        return self.add_province_interface(procedure, new_rgb, new_color_str)

Gimp.main(ProvicesPlugin.__gtype__, sys.argv)
