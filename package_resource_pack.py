import datetime
import shutil

def main():
    base_file_name = 'lang_ja_jp_hwkana-1.17-'

    date = datetime.date.today().strftime('%Y%m%d')
    zip_name = 'out/' + base_file_name + date
    shutil.make_archive(zip_name, 'zip', root_dir='src')

if __name__ == '__main__':
    main()
