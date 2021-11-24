import datetime
import glob
import json
import os
import shutil

def main():
    # Base name of pack
    base_file_name = 'lang_ja_jp_hwkana-1.17-'
    # File type of lang file, True: .json, False: .lang (now this doesn't work for 1.12)
    is_json = True

    shutil.rmtree('./temp/', ignore_errors=True)
    shutil.copytree('./src/', './temp/')
    # List .json files in src dir
    json_list = glob.glob('./temp/**/*.json', recursive=True)

    for file_name in json_list:
        data = {}
        # Load .json file from src dir
        with open(file_name, 'r', encoding='UTF-8') as f_read:
            data = json.load(f_read)

        if len(data) > 0:
            if is_json:
                # Escape Unicode characters and overwrite .json file
                with open(file_name, 'w', encoding='UTF-8') as f_json:
                    json.dump(data, f_json, ensure_ascii=True, indent=4)
            else:
                # Save as .lang file
                lang_file_name = file_name.replace('.json', '.lang')
                with open(lang_file_name, 'w', encoding='UTF-8') as f_lang:
                    for key in data:
                        f_lang.write(key + '=' + data[key] + '\n')
                os.remove(file_name)

    # Pack resources as .zip file
    date = datetime.date.today().strftime('%Y%m%d')
    zip_name = 'out/' + base_file_name + date
    shutil.make_archive(zip_name, 'zip', root_dir='temp')

if __name__ == '__main__':
    main()
