# The Farmer Was Replaced

## Setup

Delete the old directory, clone to your desired location, and symlink:

```sh
# Might be different, this is for running on Linux through Proton.
SAVE_DIR="~/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/Save0"
rm -r "$SAVE_DIR"/*
git clone https://github.com/Ahajha/tfwr.git ~/Documents/tfwr
ln -s ~/Documents/tmwr "$SAVE_DIR"
```
