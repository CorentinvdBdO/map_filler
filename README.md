GIMP plugin to create a CK3 province map

# Important message

This plug in is very ALPHA. It edits the csv files directly without verifications so always use it on a copy of your mod.

## Scope

Made for CK3. It can be expanded to other paradox GS games with the same province system, but not there yet.

Made in Linux, it should work on others OS but I won't test them myself.

For now works with csvs WITH UNIQUE IDS, such as a valid definitions.csv.

The mod is not really optimized yet and may be slow with large amount of provinces.

# Installation

Download the project (git clone or download as zip)

Put the file in your GIMP plugin folder (as /plugins/map_filler/map_filler.py)

For example on Linux you should see the whole path: `/home/cvdbdo/.config/GIMP/3.0/plug-ins/map_filler/map_filler.py`. It is important that the python `.py` is in a folder in the plug-ins folder.

Then restart GIMP, and you should see a "Provinces" menu in the top bar.

## Troubleshooting

You may need to make the file executable by running `chmod +x /home/cvdbdo/.config/GIMP/3.0/plug-ins/map_filler/map_filler.py`

For debug, launch GIMP from a terminal, so you can see the error logs.

# Usage

Edit the csv file to set your paths:
```
provinces_csv = "path/to/your/provinces.csv" 

delimiter = ";"

# Games
CK3 = "CK3"

# Modes
PROVINCES_CSV = "PROVINCES_CSV"  # A custom csv that needs to be parsed into the various files
DEFINITIONS = "DEFINITIONS"      # Directly editing the definitions files (CK3)

GAME = CK3            # Could be expanded to other paradox games
MODE = PROVINCES_CSV

ID = "id"
R = "r"
G = "g"
B = "b"
NAME = "name"
```

# How to edit game maps on Gimp
Primer on map editing on GIMP

## Save with the right format
When exporting the file, it is important to save it with the right format (prompted after the save destination is selected):

- heightmap.png: 8 bits greyscale
- provinces.png: 16 bits RGB

# Roadmap
If there is demand, if I feel like it, if there are contributors.

- Speed up for large amount of provinces
- Set parameters in game instead of in the script
- Support no Id files
- Warning for invalid csvs
- Warning for invalid province map
- Support auto edit of more files (terrains, ...)
- Support auto loading of these files into a single csv
- Support more games
- Reindexing of provinces