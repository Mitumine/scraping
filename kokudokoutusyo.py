from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
from pprint import pprint
import requests
from lxml import html
from bs4 import BeautifulSoup
import csv
import re
import sqlite3
import os

KYOKA_DICT = {
    1: '土',
    2: '建',
    3: '大',
    4: '左',
    5: 'と',
    6: '石',
    7: '屋',
    8: '電',
    9: '管',
    10: '夕',
    11: '鋼',
    12: '筋',
    13: '舗',
    14: 'しゅ',
    15: '板',
    16: 'ガ',
    17: '塗',
    18: '防',
    19: '内',
    20: '機',
    21: '絶',
    22: '通',
    23: '園',
    24: '井',
    25: '具',
    26: '水',
    27: '消',
    28: '清',
    29: '解',
}

HEADER = [
    '許可区分',
    '建設業許可番号',
    '商号又は名称',
    '営業所名',
    '代表者氏名',
    '都道府県',
    '所在地',
    '営業業態',
    '代表電話番号',
    '資本金額',
    '建設業以外の兼業の有無',
    '一般又は特定の表記',
    '許可を受けた建設業の種類',
    '許可年月',
]

WORDS = [
    'ア',
    # 'イ', 'ウ', 'エ', 'オ',
    # 'カ', 'キ', 'ク', 'ケ', 'コ',
    # 'サ', 'シ', 'ス', 'セ', 'ソ',
    # 'タ', 'チ', 'ツ', 'テ', 'ト',
    # 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    # 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    # 'マ', 'ミ', 'ム', 'メ', 'モ',
    # 'ヤ', 'ユ', 'ヨ',
    # 'ラ', 'リ', 'ル', 'レ', 'ロ',
    # 'ワ', 'ヲ', 'ン'
]

MODES = [
    '00',
    # '01'
]


def selword(word, mode, driver):
    # 検索ワード入力
    _id = 'comNameKanaOnly'
    element = driver.find_element_by_id(_id)
    element.clear()
    element.send_keys(word)

    # 大臣に選択
    _id = 'licenseNoKbn'
    element = driver.find_element_by_id(_id)
    value = mode
    Select(element).select_by_value(value)

    # 表示件数を50件に
    _id = 'dispCount'
    element = driver.find_element_by_id(_id)
    value = '50'
    Select(element).select_by_value(value)

    # 検索クリック
    xpath = '//*[@id="input"]/div[6]/div[5]/img'
    element = driver.find_element_by_xpath(xpath)
    element.click()


def write_db(data):
    DB_NAME = 'db.sqlite3'
    if os.path.exists(DB_NAME) is False:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # なかったら作成
        sql = 'create table okudo('
        for i, s in enumerate(HEADER):
            sql += f'"{s}" text'
            if i != len(HEADER) - 1:
                sql += ', '
            else:
                sql += ')'
        cur.execute(sql)
        print(sql)
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # 受け取った辞書をデータベースに記入する
    sql = f'''
    insert into okudo("{', "'.join([str(k) + '"' for k in data.keys()])})
    VALUES ("{', "'.join([str(v) + '"' for v in data.values()])})
    '''
    print(sql)
    cur.execute(sql)
    conn.commit()
    conn.close()


def main():
    options = ChromeOptions()
    options.add_argument('--headless')
    driver = Chrome(options=options)
    URL = 'https://etsuran.mlit.go.jp/TAKKEN/kensetuKensaku.do'
    driver.get(URL)

    data_list = []
    loop = True
    for mode in MODES:
        for word in WORDS:
            selword(word, mode, driver)
            while loop is True:
                for i in range(2, 51):
                    data = getdata(i, driver)
                    if data is None:
                        loop = False
                        break
                    else:
                        write_db(data)
                        del data
                        driver.back()
                xpath = '//*[@id="container_cont"]/div[7]/div[3]/img'
                element = driver.find_element_by_xpath(xpath)
                element.click()


def getdata(i, driver):
    data = {}

    # 営業所名取得
    now = '営業所名'
    xpath = f'//*[@id="container_cont"]/table/tbody/tr[{i}]/td[6]'
    try:
        element = driver.find_element_by_xpath(xpath)
        text = element.text
        data[now] = text
    except Exception:
        return None
    # 該当会社名クリック
    xpath = f'//*[@id="container_cont"]/table/tbody/tr[{i}]/td[4]/a'
    element = driver.find_element_by_xpath(xpath)
    element.click()

    # ソースコード取得してBS4にバトンタッチ
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    lxml = html.fromstring(str(soup))

    # 情報取得コーナー
    try:
        now = '許可区分'
        xpath = '//*[@id="input"]/div[1]/table/tbody/tr[1]/td'
        text = get_str_from_xpath(xpath, lxml)
        pat = '(大臣|知事)許可'
        match = re.search(pat, text).group(0)
    except TypeError:
        data = getdata(i, driver)
        return data

    data[now] = match

    now = '建設業許可番号'
    pat = '(第\d+号)'
    re.search(pat, text)
    match = re.search(pat, text).group(0)
    data[now] = match

    now = '商号又は名称'
    xpath = '/html/body/form/div/div[2]/div[5]/div/div[1]/table/tbody/tr[2]/td/text()'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '代表者氏名'
    xpath = '//*[@id="input"]/div[1]/table/tbody/tr[3]/td/text()'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '所在地'
    text = ''
    for i2 in range(2, 3):
        xpath = f'//*[@id="input"]/div[1]/table/tbody/tr[4]/td/text()[{i2}]'
        text += get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '都道府県'
    pat = '(.+?[都道府県])'
    text = re.search(pat, text).group(0)
    data[now] = text

    now = '営業業態'
    xpath = '//*[@id="input"]/div[1]/div/table/tbody/tr[1]/td'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '代表電話番号'
    xpath = '//*[@id="input"]/div[1]/table/tbody/tr[5]/td'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '資本金額'
    xpath = '//*[@id="input"]/div[1]/div/table/tbody/tr[2]/td'
    text = get_str_from_xpath(xpath, lxml)
    # カンマ消す
    text = text.replace(',', '')
    data[now] = text

    now = '建設業以外の兼業の有無'
    xpath = '//*[@id="input"]/div[1]/div/table/tbody/tr[3]/td'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    now = '一般又は特定の表記'
    ippan_tokutei_list = []
    for key in KYOKA_DICT:
        xpath = f'//*[@id="input"]/table[1]/tbody/tr[2]/td[{key}]'
        text = get_str_from_xpath(xpath, lxml)
        if text is None:
            text = str(0)
        else:
            text = str(text)
        ippan_tokutei_list.append(text)
    ippan_tokutei_list = ''.join(ippan_tokutei_list)
    data[now] = ippan_tokutei_list

    now = '許可を受けた建設業の種類'
    kyoka_list = []
    for value, key in zip(ippan_tokutei_list, KYOKA_DICT):
        if value == str(1) or value == str(2):
            kyoka_list.append(KYOKA_DICT[key])

    kyoka_list = ''.join(kyoka_list)
    data[now] = kyoka_list

    now = '許可年月'
    xpath = '//*[@id="input"]/div[2]/div[1]/div/table/tbody/tr[1]/td/a'
    text = get_str_from_xpath(xpath, lxml)
    data[now] = text

    return data


def get_str_from_xpath(xpath: str, lxml):
    '''
    受け取ったXpathが内包するinnertextをリターンする
    要lxml
    '''
    el = lxml.xpath(xpath)

    if el == []:
        return None
    else:
        try:
            return el[0].text
        except AttributeError:
            # text()用
            return str(el[0])


if __name__ == "__main__":
    main()
    # write_db()
