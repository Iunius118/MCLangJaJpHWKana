import sys
import json
from janome.tokenizer import Tokenizer    # pip install janome
import jaconv    # pip install jaconv

debug = False
debug_unknown_meishi = []

def main():
    json_object = load_json()
    translation_dict = translate(json_object)
    save_json(translation_dict)
    save_unknown_meishi()

def load_json():
    arg_list = sys.argv
    if len(arg_list) < 2:
        sys.exit("One argument representing .json file path is required.")

    if len(arg_list) > 2 and arg_list[2] == 'debug':
        global debug
        debug = True

    with open(arg_list[1], 'r', encoding='UTF-8') as f:
        return json.load(f)

    sys.exit("Could not open JSON file.")

def translate(json_object):
    dict = {}
    t = Tokenizer("user_dic.csv", udic_enc="utf8")

    for key in json_object:
        value = json_object[key]
        dict[key] = to_half_width_kana(fix_sentence(to_kana(value, t)))

    return dict

def to_kana(value, tokenizer):
    result = ''
    prev_token = None

    for token in tokenizer.tokenize(value):
        check_unknown_meishi(token)
        if needsSpace(prev_token, token):
            result += ' '

        dbg(token)
        result += getReading(token)
        prev_token = token

    return result

def needsSpace(prev_token, token):
    if prev_token is None or token is None:
        return False 
    '''
     1. 前：記号を除く（読みあり）、今：名詞・記号（読みなし）→スペースを挟む
     2. 前：名詞・記号（読みなし）、今：記号を除く（読みあり）→スペースを挟む
     3. 前：記号,空白・句点・読点を除く、今：記号,括弧開→スペースを挟む
     4. 前：記号,括弧閉、今：記号,空白を除く→スペースを挟む
     5. 前：連体詞、今：記号,空白を除く→スペースを挟む
     6. 前：記号,空白を除く、今：読み=クダサイ→スペースを挟む
     7. 前：動詞と記号,空白を除く、今：動詞,（非自立と特定の動詞を除く）→スペースを挟む
     8. 前：動詞,形容詞、今：名詞,（非自立を除く）→スペースを挟む
     8.1. 前：副詞、今：名詞→スペースを挟む
     8.2. 前：形容詞,名詞（助数詞）、今：名詞（非自立と接尾を除く）→スペースを挟む
     9. 前：非自立語（記号を除く）、今：自立語（非自立と読みなしを除く）→スペースを挟む
    10. 前：自立語（非自立を除く）、今：自立語（同品詞と非自立と読みなしを除く）→スペースを挟む
    ※自立語=名詞、動詞、形容詞、形容動詞、副詞、連体詞、接続詞、感動詞
    '''
    jiritsu_tags = ['名詞', '接頭詞', '動詞', '形容詞', '形容動詞', '副詞', '連体詞', '接続詞', '感動詞']
    jiritsu_tags_2 = ['名詞', '接頭詞', '動詞', '形容詞', '形容動詞', '副詞', '連体詞', '接続詞', '感動詞', '記号']
    no_spacing_doshi_1 = ['する', 'なる']
    no_spacing_doshi_2 = ['ある', 'いる']
    spacing_joshi = ['が', 'に', 'の', 'は', 'も']
    prev_pos = prev_token.part_of_speech.split(',')
    pos = token.part_of_speech.split(',')
    if prev_pos[1] == '空白' or prev_pos[1] == '括弧開' or prev_pos[1] == '句点' or prev_pos[1] == '読点' or prev_token.surface == '…' or pos[1] == '句点' or pos[1] == '読点':
        return False
    elif prev_pos[1] == '括弧閉' and pos[1] == '括弧開':
        return False
    elif prev_pos[0] != '記号' and hasReading(prev_token) and not hasReading(token):
        dbg('Spacing: 1')
        return True
    elif not hasReading(prev_token) and pos[0] != '記号' and hasReading(token):
        dbg('Spacing: 2')
        return True
    elif pos[1] == '括弧開':
        dbg('Spacing: 3')
        return True
    elif prev_pos[1] == '括弧閉' and prev_pos[1] != '空白':
        dbg('Spacing: 4')
        return True
    elif prev_pos[0] == '連体詞':
        dbg('Spacing: 5')
        return True
    elif token.reading == 'クダサイ':
        dbg('Spacing: 6')
        return True
    elif prev_pos[0] != '動詞' and prev_pos[0] != '記号' and prev_pos[0] != '接頭詞' and isJiritsu(pos, ['動詞']):
        flag_no_spacing = token.base_form in no_spacing_doshi_1 or (token.base_form in no_spacing_doshi_2 and (prev_pos[0] == '助詞' and prev_token.base_form not in spacing_joshi))
        if flag_no_spacing:
            dbg('No spacing: 7')
        else:
            dbg('Spacing: 7')
        return not flag_no_spacing
    elif prev_pos[0] == '動詞' and isJiritsu(pos, ['名詞']):
        dbg('Spacing: 8')
        return True
    elif prev_pos[0] == '副詞' and pos[0] == '名詞':
        dbg('Spacing: 8.1')
        return True
    elif (prev_pos[0] == '形容詞' or prev_pos[2] == '助数詞') and pos[0] == '名詞':
        no_spacing_2nd_tags = ['非自立', '接尾']
        flag_no_spacing = pos[1] in no_spacing_2nd_tags
        if flag_no_spacing:
            dbg('No spacing: 8.2')
        else:
            dbg('Spacing: 8.2')
        return not flag_no_spacing
    elif (not isJiritsu(prev_pos, jiritsu_tags_2) and prev_pos[1] != '非自立') and isJiritsu(pos, jiritsu_tags) and hasReading(token):
        dbg('Spacing: 9')
        return True
    elif isJiritsu(prev_pos, jiritsu_tags) and isJiritsu(pos, jiritsu_tags) and ((prev_pos[0] != pos[0] and not (prev_pos[0] == '接頭詞' and (pos[0] == '名詞' or pos[0] == '動詞'))) or (prev_pos[0] == '副詞' or prev_pos[0] == '形容詞') and (pos[0] == '副詞' or pos[0] == '形容詞')) and hasReading(token):
        dbg('Spacing: 10')
        return True
    else:
        return False

def isJiritsu(pos, tags):
    return pos[1] != '非自立' and pos[0] in tags

def hasReading(token):
    return token.reading != '*'

def getReading(token):
    result = token.reading
    if result != '*':
        return result
    else:
        return token.surface

def fix_sentence(value):
    if value == 'テキ':
        return 'マト'
    if value == 'ヒ':
        return 'ニチ'
    if value == 'ソラ':
        return 'カラ'

    result = value.replace('s ヒト', 's ニン').replace('s ジン', 's ニン').replace('s カラダ', 's タイ').replace(' ：', '：').replace('：%', '： %').replace('：ヒ', '： ヒ').replace('s：', 's： ').replace('ID%', 'ID %').replace('チュウイ：', 'チュウイ： ').replace('ケイコク：', 'ケイコク： ').replace('← ', '<-').replace('→', '->').replace('…', '・・・').replace('  ', ' ')

    if result == 'チュウイ： ':
        return 'チュウイ：'
    if result == '↑ ↓':
        return '↑↓'

    return result

def to_half_width_kana(value):
    result = jaconv.z2h(value, kana = True, digit = True, ascii = True)
    return result

def save_json(translation_dict):
    with open("out.txt", "w", encoding='UTF-8') as f:
        json.dump(translation_dict, f, ensure_ascii=False, indent=4)

def check_unknown_meishi(token):
    if not debug:
        return

    pos = token.part_of_speech.split(',')
    if pos[0] != '名詞' or hasReading(token):
        return

    meishi = token.surface

    global debug_unknown_meishi
    if meishi not in debug_unknown_meishi:
        debug_unknown_meishi.append(meishi)

def save_unknown_meishi():
    global debug_unknown_meishi
    if len(debug_unknown_meishi) < 1:
        return

    with open("out_mis.txt", "w", encoding='UTF-8') as f:
        for meishi in sorted(debug_unknown_meishi):
            f.write(meishi + '\n')

def dbg(mes):
    if debug:
        print(mes)

if __name__ == "__main__":
    main()
