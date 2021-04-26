from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
from pprint import pprint
import requests
from lxml import html
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import re
from multiprocessing import Pool


def get_url():
    options = ChromeOptions()
    # options.add_argument('--headless')
    driver = Chrome(options=options)

    URL = 'https://www.hellowork.mhlw.go.jp/kensaku/GECA110010.do?action=initDisp&screenId=GECA110010'
    driver.get(URL)
    url_list = []
    startpoint = 1
    endpoint = 50

    # # 都道府県セット
    # id_box = 'ID_tDFK1CmbBox'
    # box_element = driver.find_element_by_id(id_box)
    # Select(box_element).select_by_value('13')

    input('おkならEnter')

    # 検索
    driver.find_element_by_id('ID_searchBtn').click()

    # 表示件数を50件に
    id_box = 'ID_fwListNaviDispTop'
    box_element = driver.find_element_by_id(id_box)
    Select(box_element).select_by_value('50')

    page = 0
    with tqdm(total=endpoint) as t:
        for _ in range(1, endpoint):
            page += 1
            t.update(1)
            if endpoint == page:
                break
            elif startpoint <= page:
                for i in range(4, 53):
                    #  /html/body/div/div/form/table[29]/tbody/tr[6]/td/div/a
                    try:
                        xpath = f'/html/body/div/div/form/table[{i}]/tbody/tr[.]/td/div/a[2]'
                        syousai = driver.find_element_by_xpath(xpath)
                    except Exception:
                        xpath = f'/html/body/div/div/form/table[{i}]/tbody/tr[6]/td/div/a[2]'
                        syousai = driver.find_element_by_xpath(xpath)
                    url_list.append(syousai.get_attribute('href'))
                name = 'fwListNaviBtnNext'
            elif page <= 5:
                name = 'fwListNaviBtn6'
                page += 4
                t.update(4)
            elif page > 5:
                name = 'fwListNaviBtn7'
                page += 4
                t.update(4)

            driver.find_element_by_name(name).click()

    url_list = [[x] for x in url_list]
    return url_list


def kyuujinhyou(URL):

    # 渡辺さん用
    XPATHS = {
        '社名': '//*[@id="ID_jgshMei"]',
        '種別': '',
        '会社ホームページ': '//*[@id="ID_hp"]',
        'メールアドレス': '',
        '問い合わせフォーム': '',
        '抽出元': '',

    }

    # マイナビ用
    # XPATHS = {
    #     '抽出元': '',
    #     '社名': '//*[@id="ID_jgshMei"]',
    #     '電話番号': '//*[@id="ID_ttsTel"]',
    #     '住所': '//*[@id="ID_szci"]',
    #     '従業員人数': '//*[@id="ID_jgisKigyoZentai"]',
    #     '代表者名': '//*[@id="ID_dhshaMei"]',
    #     'メールアドレス': '',
    #     '会社ホームページ': '//*[@id="ID_hp"]',
    # }

    # # 前の方はこっち
    # XPATHS = {
    #     '事業所名': '//*[@id="ID_jgshMei"]',
    #     'url': '',
    #     '就業場所': '//*[@id="ID_shgBsJusho"]',
    #     '従業員人数': '//*[@id="ID_jgisKigyoZentai"]',
    #     '代表者名': '//*[@id="ID_dhshaMei"]',
    #     '採用担当者名': '//*[@id="ID_ttsTts"]',
    #     '電話番号': '//*[@id="ID_ttsTel"]',
    # }

    while True:
        try:
            res = requests.get(URL)
            break
        except:
            pass

    soup = BeautifulSoup(res.text, 'html.parser')
    lxml = html.fromstring(str(soup))
    texts = []
    for key in XPATHS:
        xpath = XPATHS[key]
        if key == 'url':
            text = URL
        elif key == '従業員人数':
            text = get_str_from_xpath(xpath, lxml)
            try:
                text = re.sub('(\d)人', '\\1', text)
            except:
                pass
        elif key == '会社ホームページ':
            text = get_str_from_xpath(xpath, lxml)
            try:
                text = re.sub('\s*\n*\s*', '', text)
            except:
                pass
        elif key == '代表者名_a':
            text = get_str_from_xpath(xpath, lxml)
            if text != '':
                text = f'会社代表:{text}'
            continue
        elif key == '代表者名_b':
            text = get_str_from_xpath(xpath, lxml)
            if text != '':
                text = f'担当者:{text}'
        elif key == '抽出元':
            # text = 'ハローワーク50-100名'
            text = 'https://www.hellowork.mhlw.go.jp/'
        elif xpath == '':
            text = ''
        else:
            text = get_str_from_xpath(xpath, lxml)

        texts.append(text)

    return texts


def main():
    urls = get_url()

    with open('urls.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(urls)

    with open('urls.csv') as f:
        urls = [x[0] for x in csv.reader(f)]

    texts = []

    # テスト用
    # for url in tqdm(urls):
    #     res = kyuujinhyou(url)
    #     texts.append(res)

    pool = Pool(processes=20)
    with tqdm(total=len(urls)) as t:
        for res in pool.imap_unordered(kyuujinhyou, urls):
            texts.append(res)
            t.update(1)

    write_csv(texts, 'datas.csv')


def write_csv(write_list: dict, path: str):
    '''
    渡された引数の辞書をリストに変換してCSVに書き込む
    '''

    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(write_list)


def get_str_from_xpath(xpath: str, lxml):
    '''
    受け取ったXpathが内包するテキストをリターンする
    要lxml
    '''
    el = lxml.xpath(xpath)

    if el == []:
        return ''
    else:
        try:
            return el[0].text
        except AttributeError:
            # text()用
            return str(el[0])


if __name__ == "__main__":
    main()
