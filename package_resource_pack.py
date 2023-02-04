import datetime
import glob
import json
import os
import shutil

def main():
    # Base name of pack
    base_file_name = 'lang_ja_jp_hwkana'
    json_ver_mod = '-1.19.3-'
    # File type of lang file, True: .json, False: .lang
    # * 1.12 is outdated
    # lang_ver_mod = '-1.12-'
    is_json = True

    # Copy src/ to temp/
    shutil.rmtree('./temp/', ignore_errors=True)
    shutil.copytree('./src/', './temp/')

    if is_json:
        gen_json_ver('temp')
        package_resource('temp', base_file_name + json_ver_mod)
    # else:
        # Outdated!
        # gen_lang_ver('temp')
        # package_resource('temp', base_file_name + lang_ver_mod)

def gen_json_ver(src_dir):
    # List .json files in src dir
    json_list = glob.glob(src_dir + '/**/*.json', recursive=True)

    for file_name in json_list:
        data = {}
        # Load .json file from src dir
        with open(file_name, 'r', encoding='UTF-8') as f_read:
            data = json.load(f_read)

        if len(data) > 0:
            # Escape Unicode characters and overwrite .json file
            with open(file_name, 'w', encoding='UTF-8') as f_json:
                json.dump(data, f_json, ensure_ascii=False, indent=4)

def gen_lang_ver(src_dir):
    # Fix pack format version
    data = {}

    with open('temp/pack.mcmeta', 'r', encoding='UTF-8') as f_read:
        data = json.load(f_read)
        # Pack format 3 for 1.11 - 1.12.2
        data['pack']['pack_format'] = 3

    if len(data) > 0:
        with open('temp/pack.mcmeta', 'w', encoding='UTF-8') as f_json:
            json.dump(data, f_json, ensure_ascii=False, indent=2)

    # Generate lang files
    cnv_table = {}
    ex_values = {}

    with open('data/table_1.12_to_1.17.json', 'r', encoding='UTF-8') as f_read:
        cnv_table = json.load(f_read)

    with open('data/table_1.12_ex.json', 'r', encoding='UTF-8') as f_read:
        ex_values = json.load(f_read)

    # List .json files in src dir
    json_list = glob.glob(src_dir + '/**/*.json', recursive=True)

    for file_name in json_list:
        if 'minecraft' in file_name:
            # Generate Minecraft lang
            gen_lang_file(file_name, 'data/table_1.12_mc_keys.json', cnv_table, ex_values)
        elif 'realms' in file_name:
            # Generate Realms lang
            gen_lang_file(file_name, 'data/table_1.12_re_keys.json', cnv_table, ex_values)

def gen_lang_file(json_name, key_list_json_name, cnv_table, ex_values):
    data_in = {}
    data_out = {}
    with open(json_name, 'r', encoding='UTF-8') as f_read:
        data_in = json.load(f_read)

    with open(key_list_json_name, 'r', encoding='UTF-8') as f_read:
        json_data = json.load(f_read)
        key_list = json_data['keys']

        for key in key_list:
            cnv_key = cnv_table[key]
            value = ''

            if cnv_key in data_in:
                value = data_in[cnv_key]

            elif key in ex_values:
                value = ex_values[key]
            
            if len(value) > 0:
                data_out[key] = value
            else:
                print('Error: key ' + key + ' is not found')

        lang_name = json_name.replace('.json', '.lang')
        with open(lang_name, 'w', encoding='UTF-8') as f_lang:
            for key in data_out:
                f_lang.write(key + '=' + data_out[key] + '\n')

        os.remove(json_name)


def package_resource(src_dir, base_file_name):
    # Pack resources as .zip file
    date = datetime.date.today().strftime('%Y%m%d')
    zip_name = 'out/' + base_file_name + date
    shutil.make_archive(zip_name, 'zip', root_dir=src_dir)

if __name__ == '__main__':
    main()
