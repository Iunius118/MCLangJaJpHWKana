import argparse
import os
import json

def _main():
    args = _get_args()
    index_path = get_index_path(args.mc_path, args.mc_ver)
    print(f'Get ja_jp.jang from {index_path}')
    get_ja_jp_json(args.mc_path, args.mc_ver, args.mc_ver_output)

def _get_args():
    parser = argparse.ArgumentParser(description='Get ja_jp json files from cache of Minecraft assets.')
    parser.add_argument('--mc_ver', help='Minecraft version', default='1.19')
    parser.add_argument('--mc_ver_output', help='Minecraft version for name of output file', default='1.19.2')
    parser.add_argument('--mc_path', help='Path to .minecraft directory. Default value is suitable for Windows.', default=os.path.join(os.path.expanduser('~'), f'AppData{os.sep}Roaming{os.sep}.minecraft'))
    args = parser.parse_args()
    return args

def get_ja_jp_json(mc_path: str, mc_ver: str, mc_ver_output: str):
    index_path = get_index_path(mc_path, mc_ver)
    index_objects = get_index_json(index_path)['objects']
    lang_ext = 'json' if float(mc_ver) > 1.12 else 'lang'

    mc_lang_hash = index_objects[f'minecraft/lang/ja_jp.{lang_ext}']['hash']
    mc_lang_path = get_object_path(mc_path, mc_lang_hash)

    with open(mc_lang_path, 'r', encoding='utf-8') as f:
        print(f'Open {mc_lang_path} as Minecraft lang file')
        mc_lang = f.read()
        mc_lang_filename = mc_ver_output + '_mc_ja_jp.json'
        with open(mc_lang_filename, 'w', encoding='utf-8') as fo:
            fo.write(mc_lang)

    if f'realms/lang/ja_jp.{lang_ext}' not in index_objects:
        return

    realms_lang_hash = index_objects[f'realms/lang/ja_jp.{lang_ext}']['hash']
    realms_lang_path = get_object_path(mc_path, realms_lang_hash)

    with open(realms_lang_path, 'r', encoding='utf-8') as f:
        print(f'Open {realms_lang_path} as Realms lang file')
        realms_lang = f.read()
        realms_lang_filename = mc_ver_output + '_re_ja_jp.json'
        with open(realms_lang_filename, 'w', encoding='utf-8') as fo:
            fo.write(realms_lang)

def get_index_path(mc_path: str, mc_ver: str):
    return os.path.join(mc_path, f'assets{os.sep}indexes', mc_ver + '.json')

def get_object_path(mc_path: str, object_hash: str):
    return os.path.join(mc_path, f'assets{os.sep}objects', object_hash[:2], object_hash)

def get_index_json(index_path: str):
    index_json = {}

    with open(index_path, 'r') as f:
        index_json = json.load(f)

    return index_json

if __name__ == "__main__":
    _main()
