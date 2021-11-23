import datetime
import glob
import json
import os
import shutil

def main():
    base_file_name = 'lang_ja_jp_hwkana-1.17-'

    shutil.rmtree('./temp/', ignore_errors=True)
    shutil.copytree('./src/', './temp/')

    json_list = glob.glob('./temp/**/*.json', recursive=True)
    for file_name in json_list:
        data = {}
        with open(file_name, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        if len(data) > 0:
            with open(file_name, 'w', encoding='UTF-8') as f:
                json.dump(data, f, ensure_ascii=True, indent=4)

    date = datetime.date.today().strftime('%Y%m%d')
    zip_name = 'out/' + base_file_name + date
    shutil.make_archive(zip_name, 'zip', root_dir='temp')

if __name__ == '__main__':
    main()
