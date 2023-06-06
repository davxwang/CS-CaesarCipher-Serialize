# CS-CaesarCipher-Serialize
Counterside tool for serializing and organizing the game files for reading or further processing

Requires Python 3.x and Lua.

1. Drop the "TextAsset" folder with the encrypted LUA file names from assetstudio into "Encoded"
2. Run CS_CaesarCipher+Serialize.py
3. Wait (may take some time if you threw in all scripts)
4. Serialized lua table files with decrypted file names will be found in "Decoded"

## config.ini

If something breaks while touching the config file, delete it then rerun the script to regenerate it.

### [LUA]

"lua_alias" is for if you've aliased your lua path something else.

"path_lua_serializetable" is the relative path to the SerializeTable.lua file normally found in .\CS_CaesarCipher+Serialize. Change if you move these.

### [FLAG]

"flag_write_all" Does not sort/organize the files. It just drops everything in the decoded folder.

"flag_write_view" My preferred setup for manually examining units and stuff.

"flag_write_view_other" Drop all files that I don't particularly care about into "other" within "view". Only does anything if flag_write_view is set to True. It is redundant to turn both these two and flag_write_all on.

"flag_write_sheet" The mininum about of files needed for my spreadsheet generation script on player units.

"flag_write_prydwen" Processes specific files according to the parameter further down. 

### [FILE_DIRECTORY]
"directory_encoded" and "directory_decoded" are the relative path to the encoded and decoded folders. They can be renamed here without issue, but the subfolder names are hardcoded in the python script.

### [PRYDWEN]
"filename:folder_in_prydwen" Specifies the files to be processed when flag_write_prydwen is set to True. Filename is the decrypted name of the file. Folder_in_prydwen is the subfolder within the prydwen folder that the file is to be sent to. "." and blank (both "" and " ") defaults to the base prydwen folder. The two are separated by ":", and each entry is delimited by ",".
