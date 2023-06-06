import os
import shutil
import subprocess
import configparser

# alphabet dictionary. I would have just done {chr(i+64):i for i in range(26)}, but I FORGOT TO GOOGLE FIRST GODDAMMIT
alphabet = dict(
    [('A', 0), ('B', 1), ('C', 2), ('D', 3), ('E', 4), ('F', 5), ('G', 6), ('H', 7), ('I', 8), ('J', 9), ('K', 10),
     ('L', 11),
     ('M', 12), ('N', 13), ('O', 14), ('P', 15), ('Q', 16), ('R', 17), ('S', 18), ('T', 19), ('U', 20), ('V', 21),
     ('W', 22),
     ('X', 23), ('Y', 24), ('Z', 25)])
# lowercase alphabet dictionary. ('a', 0) .. ('z', 25)
alphabet_lower = dict({chr(i+97):i for i in range(26)})

# calculates the offset to the key
# returns int: key_offset
def calc_key_offset(string_length, charset_length):
    key_offset = string_length//charset_length

    # second offset is 3 at every multiple of (charset_length - 1), and 1 for a certain number of lengths after the 3
    # the number of trailing 1s increase after every instance of 3
    second_offset_interval = string_length % (charset_length - 1)
    if second_offset_interval == 0:
        return key_offset + 3
    elif second_offset_interval <= string_length//(charset_length - 1) - 1:
        return key_offset + 1
    else:
        return key_offset


# encodes plaintext into ciphertext
# returns string: plaintext
def encode(plaintext):
    ciphertext = ""

    for letter in plaintext:
        if letter == '_' or letter == '.' or letter == ' ':
            ciphertext += letter
        elif letter.isnumeric():
            key_offset = calc_key_offset(len(plaintext), 10)
            ciphertext += str((int(letter) + len(plaintext) + key_offset)%10)
        #legacy section from when upper and lowercase ciphers were different. Remove if it never goes back.
        elif letter.islower():
            key_offset = calc_key_offset(len(plaintext), 26)
            ciphertext += list(alphabet_lower.keys())[((alphabet_lower[letter] + len(plaintext) + key_offset) % 26)]
        else:
            key_offset = calc_key_offset(len(plaintext), 26)
            ciphertext += list(alphabet.keys())[((alphabet[letter] + len(plaintext) + key_offset)%26)]

    return ciphertext


# decodes ciphertext into plaintext
# returns string: plaintext
def decode(ciphertext):
    plaintext = ""

    for letter in ciphertext:
        if letter == '_' or letter == '.' or letter == ' ':
            plaintext += letter
        elif letter.isnumeric():
            key_offset = calc_key_offset(len(ciphertext), 10)
            plaintext += str((int(letter) - len(ciphertext) - key_offset)%10)
        #legacy section from when upper and lowercase ciphers were different. Remove if it never goes back.
        elif letter.islower():
            key_offset = calc_key_offset(len(ciphertext), 26)
            plaintext += list(alphabet_lower.keys())[((alphabet_lower[letter] - len(ciphertext) - key_offset)%26)]
        else:
            key_offset = calc_key_offset(len(ciphertext), 26)
            plaintext += list(alphabet.keys())[((alphabet[letter] - len(ciphertext) - key_offset)%26)]

    return plaintext


# serializes the lua file at the file_path assuming it is a table
# returns the serialized contents, and the name of the table
def serialize_file(file_path):
    # script generates 'temp_serialized.txt' at the same directory, which is a serialized lua table
    subprocess.run([LUA_ALIAS, os.path.basename(PATH_LUA_SerializeTable), os.path.abspath(file_path)],
                   check=True, cwd=os.path.dirname(PATH_LUA_SerializeTable))

    # debug - decrypted name
    # print(new_name_path + '\n')

    # read all
    with open(os.path.dirname(PATH_LUA_SerializeTable) + '\\temp_serialized.txt',
              'r', encoding='utf-8') as f_input:
        new_file_contents = f_input.read()

    # table information for selective write
    with open(os.path.dirname(PATH_LUA_SerializeTable) + '\\temp_serialized_tablename.txt',
              'r', encoding='utf-8') as f_input_type:
        # only read a single line for files with multiple tables
        table_name = f_input_type.readline()

    return new_file_contents, table_name


# main
# read config file
config = configparser.ConfigParser(allow_no_value = True, delimiters = ('=',))
# create config file if it was lost somehow
if not config.read('config.ini'):
    config['LUA'] = {'LUA_ALIAS': 'lua', 'PATH_LUA_SerializeTable': '.\\SerializeTable.lua'}

    config['FLAG'] = {'FLAG_WRITE_ALL': 'True', 'FLAG_WRITE_VIEW': 'True', 'FLAG_WRITE_VIEW_OTHER': 'True',
                      'FLAG_WRITE_SHEET': 'True', 'FLAG_WRITE_PRYDWEN': 'True'}
    config['FILE_DIRECTORY'] = {'directory_encoded': '.\\Encoded', 'directory_decoded': '.\\Decoded'}
    config['PRYDWEN'] = {'filename:folder_in_prydwen': 'LUA_BUFF_TEMPLET2:.,LUA_SI_COLLECTION_UNIT_INTRO_KOREA:.,'
                                              'LUA_SI_OPR_SKILL_KOREA:.,LUA_SI_UNIT_KOREA:.,'
                                              'LUA_SI_UNIT_SKILL_KOREA:.,LUA_STRING_ENG:.,'
                                              'LUA_UNIT_SKILL_TEMPLET:.,LUA_UNIT_STAT_TEMPLET:.,'
                                              'LUA_UNIT_TEMPLET_BASE:.'}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# lua related consts
LUA_ALIAS = config['LUA']['LUA_ALIAS']
PATH_LUA_SerializeTable = config['LUA']['PATH_LUA_SerializeTable']

# flags
# write everything
FLAG_WRITE_ALL = config['FLAG'].getboolean('FLAG_WRITE_ALL')
# output view sorted folder. My preferred structure for looking up information manually.
FLAG_WRITE_VIEW = config['FLAG'].getboolean('FLAG_WRITE_VIEW')
# output view's Other folder. Somewhat useful if WRITE_ALL is turned off as useless files will go here.
FLAG_WRITE_VIEW_OTHER = config['FLAG'].getboolean('FLAG_WRITE_VIEW_OTHER')
# output sheet sorted folder. File structure for my script that compiles information into csv files for spreadsheeting.
FLAG_WRITE_SHEET = config['FLAG'].getboolean('FLAG_WRITE_SHEET')
# output prydwen sorted folder. Holds only files specified by prydwen devs.
FLAG_WRITE_PRYDWEN = config['FLAG'].getboolean('FLAG_WRITE_PRYDWEN')

# root directory names
directory_encoded = config['FILE_DIRECTORY']['directory_encoded']
directory_decoded = config['FILE_DIRECTORY']['directory_decoded']

# sorted/filtered root folders
directory_view = directory_decoded + '\\' + 'view'
directory_sheet = directory_decoded + '\\' + 'sheet'
directory_prydwen = directory_decoded + '\\' + 'prydwen'

# verify root level directory existence
if not os.path.isdir(directory_encoded):
    os.mkdir(directory_encoded)
if not os.path.isdir(directory_decoded):
    os.mkdir(directory_decoded)

# prydwen file dictionary. Key is file name, value is path to store the file relative to prydwen folder.
dict_prydwen_files = {}
if FLAG_WRITE_PRYDWEN:
    # check directory
    if not os.path.isdir(directory_prydwen):
        os.mkdir(directory_prydwen)

    for pair in config['PRYDWEN']['filename:folder_in_prydwen'].split(','):
        key, temp_value = pair.split(':', 1)

        # process temp_value into a path
        value = directory_prydwen
        list_steps = temp_value.split('\\')

        # compensates for some poorly entered names
        if len(list_steps) > 0 and list_steps[-1] == '':
            list_steps.pop(-1)
        # if the first index is a dot representing current directory, or other known malformed shenanigans
        if len(list_steps) > 0 and any([list_steps[0] == '.', list_steps[0] == '', list_steps[0] == ' ']):
            list_steps.pop(0)

        # build path
        for step in list_steps:
            # verify and create directory
            if not os.path.isdir(value + '\\' + step):
                os.mkdir(value + '\\' + step)
            # append
            value += '\\' + step

        dict_prydwen_files[key] = value

# verify other directory existence
# input folder in encoded
if not os.path.isdir(directory_encoded + '\\TextAsset'):
    os.mkdir(directory_encoded + '\\TextAsset')
# viewing directory structure
tuple_directory_view = (directory_view, directory_view + '\\Dungeons', directory_view + '\\Monsters and ships',
                        directory_view + '\\Units')
# viewing directory structure add on for other
tuple_directory_view_other = (directory_view + '\\Other', directory_view + '\\Other\\Cutscene',
                              directory_view + '\\Other\\WarfareChess')
# sheet creation directory structure
tuple_directory_sheet = (directory_sheet, directory_sheet + '\\Detail', directory_sheet + '\\Detail\\Damage',
                         directory_sheet + '\\Lang', directory_sheet + '\\Unit')
# verify
list_directories = []
if FLAG_WRITE_SHEET:
    list_directories.append(tuple_directory_sheet)
if FLAG_WRITE_VIEW:
    list_directories.append(tuple_directory_view)
if FLAG_WRITE_VIEW and FLAG_WRITE_VIEW_OTHER:
    list_directories.append(tuple_directory_view_other)
for tuple_directory in list_directories:
    for path_directory in tuple_directory:
        if not os.path.isdir(path_directory):
            os.mkdir(path_directory)

#debug - string for skipped files
string_skipped = ''

for file in os.scandir(directory_encoded + '\\TextAsset'):
    if file.is_file:
        name, ext = os.path.splitext(file.name)

        # in case any non-lua files get mixed in
        if ext == '.lua' or ext == '.luac':
            #old lowercase stuff. Remove during rewrite.
            #if not name.isupper() and not (name.find('XUW_ZRKCO_OFOXD_RYBSJYX_') != -1 and name.find('kfo') != -1):
            #if name.find(' ') != -1:
            if False:
                #debug - skipped file
                string_skipped += file.name + '\n'
            else:
                #debug - encrypted name
                #print(file.name)

                # fix file extension
                if ext == '.luac':
                    ext = '.lua'

                # decode name
                if name != "LUA_ASSET_BUNDLE_FILE_LIST":
                    new_name = decode(name)
                else:
                    new_name = name

                # build new path
                new_name_path = new_name + ext

                # if prydwen is the only flag, then delay serialization
                serialized = False
                new_file_contents = ''
                table_name = ''
                if any([FLAG_WRITE_ALL, FLAG_WRITE_VIEW, FLAG_WRITE_VIEW_OTHER, FLAG_WRITE_SHEET]):
                    new_file_contents, table_name = serialize_file(file.path)

                    serialized = True

                # write all
                if FLAG_WRITE_ALL:
                    with open(directory_decoded + '\\' + new_name_path, 'w', encoding='utf-8') as f_output:
                        f_output.write(new_file_contents)

                # selective write
                # only run these checks if either of these flags are raised
                if FLAG_WRITE_SHEET or FLAG_WRITE_VIEW:
                    # tracks whether it was written to view
                    view_written = False

                    # constants
                    # targets: view
                    if new_name == 'LUA_COMMON_CONST':
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # heals
                    # targets: view
                    if new_name == 'LUA_COMMON_UNIT_EVENT_HEAL':
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # units
                    # targets: sheet, view
                    if table_name == 'NKMUnitTemplet':
                        if new_name.find('NKM_UNIT_') != -1 and all([new_name.find('_TUTORIAL_') == -1,
                                                                     new_name != 'NKM_UNIT_TRAINER_DUMMY',
                                                                     new_name != 'NKM_UNIT_C_JOO_SHI_YOON_TR',
                                                                     new_name.find('_TR_NO') == -1]):
                            # sheet takes the base units too
                            if FLAG_WRITE_SHEET:
                                with open(directory_sheet + '\\Unit\\' + new_name_path,
                                          'w', encoding='utf-8') as f_output:
                                    f_output.write(new_file_contents)
                            # view puts base units in monsters and ships
                            if FLAG_WRITE_VIEW:
                                if new_name.find('NKM_UNIT_BASE_') == -1:
                                    with open(directory_view + '\\Units\\' + new_name_path,
                                              'w', encoding='utf-8') as f_output:
                                        f_output.write(new_file_contents)
                                        view_written = True
                                else:
                                    with open(directory_view + '\\Monsters and ships\\' + new_name_path,
                                              'w', encoding='utf-8') as f_output:
                                        f_output.write(new_file_contents)
                                        view_written = True
                        # monsters and ships
                        else:
                            with open(directory_view + '\\Monsters and ships\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # dungeons
                    # targets: view
                    if new_name == 'LUA_DUNGEON_TEMPLET_BASE' or new_name == 'LUA_MAP_TEMPLET' or table_name == 'NKMDungeonTemplet':
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\Dungeons\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # damage related files. LUA_DAMAGE_TEMPLET, LUA_DAMAGE_TEMPLET_BASE, LUA_DAMAGE_EFFECT_TEMPLET
                    # targets: sheet, view
                    if new_name.find('LUA_DAMAGE_') != -1:
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Detail\\Damage\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # buffs
                    # targets: sheet, view
                    if new_name.find('LUA_BUFF_TEMPLET') != -1:
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # animation timings
                    # targets: sheet, view
                    if new_name == 'LUA_ANIM_DATA':
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # animation timings
                    # targets: sheet, view
                    if new_name.find('LUA_UNIT_TEMPLET_BASE') != -1:
                        if FLAG_WRITE_SHEET and new_name == 'LUA_UNIT_TEMPLET_BASE':
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # skill templet
                    # targets: sheet, view
                    if new_name == 'LUA_UNIT_SKILL_TEMPLET':
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # stat templet
                    # targets: sheet, view
                    if new_name.find('LUA_UNIT_STAT_TEMPLET') != -1:
                        if FLAG_WRITE_SHEET and new_name == 'LUA_UNIT_STAT_TEMPLET':
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # base unit templet
                    # targets: sheet, view
                    if new_name.find('LUA_UNIT_TEMPLET_BASE') != -1:
                        if FLAG_WRITE_SHEET and new_name == 'LUA_UNIT_TEMPLET_BASE':
                            with open(directory_sheet + '\\Detail\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # lang kr unit names
                    # targets: sheet, view
                    if new_name == 'LUA_SI_UNIT_KOREA':
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Lang\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # lang english
                    # targets: sheet, view
                    if new_name == 'LUA_STRING_ENG':
                        if FLAG_WRITE_SHEET:
                            with open(directory_sheet + '\\Lang\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                        if FLAG_WRITE_VIEW:
                            with open(directory_view + '\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # cutscenes
                    if table_name == 'm_dicNKCCutScenTempletByID':
                        if FLAG_WRITE_VIEW and FLAG_WRITE_VIEW_OTHER:
                            with open(directory_view + '\\Other\\Cutscene\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # warfare
                    # targets: view
                    if new_name == 'LUA_WARFARE_TEMPLET' or table_name == 'NKMWarfareMapTemplet':
                        if FLAG_WRITE_VIEW and FLAG_WRITE_VIEW_OTHER:
                            with open(directory_view + '\\Other\\WarfareChess\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True

                    # unsorted for view
                    # targets: view
                    if not view_written:
                        if FLAG_WRITE_VIEW and FLAG_WRITE_VIEW_OTHER:
                            with open(directory_view + '\\Other\\' + new_name_path,
                                      'w', encoding='utf-8') as f_output:
                                f_output.write(new_file_contents)
                                view_written = True
                # prydwen specific check
                if FLAG_WRITE_PRYDWEN:
                    if new_name in dict_prydwen_files:
                        # make sure the file is serialized
                        if not serialized:
                            new_file_contents, table_name = serialize_file(file.path)
                            serialized = True

                        with open(dict_prydwen_files[new_name] + '\\' + new_name_path,
                                  'w', encoding='utf-8') as f_output:
                            f_output.write(new_file_contents)

        else:
            #debug - skipped non-lua file
            string_skipped += file.name + '\n'
            continue
    else:
        #debug - skipped non-file
        string_skipped += file.name + '\n'
        continue

#debug
with open('skipped_files.txt', 'w', encoding='utf-8') as f_output:
    f_output.write(string_skipped)
