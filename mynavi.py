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

    URL = 'https://job.mynavi.jp/22/pc/corpinfo/displayCorpSearch/index'
    driver.get(URL)
    url_list = []

    # 都道府県セット

    # この番号にヒットしたら除外する
    # dame_list = list(range(17, 20)) + list(range(27, 30)) + \
    #     list(range(36, 40)) + list(range(44, 50)) + \
    #     list(range(56, 60)) + list(range(67, 70)) + \
    #     list(range(78, 80)) + [25, 26, 43, 52, 53, ]

    dame_list = list(range(10, 23)) + list(range(27, 99))

    for i1 in range(1, 7):
        # js = f'fncRegionalNameLink(this, "areaGroup{i1 - 1}");'
        # driver.execute_script(js)
        for i2 in range(0, 10):
            i12 = int(f'{i1}{i2}')
            if i12 not in dame_list:
                # Jsを直接叩く
                _id = f'#ifRegional5{i12}'
                js = f'document.querySelector("{_id}").checked = true;'
                driver.execute_script(js)
                # driver.find_element_by_xpath(xpath).click()

    _id = 'doSearchTypeIndustryArea2'
    driver.find_element_by_id(_id).click()

    _id = 'specifyDetailInd'
    driver.find_element_by_id(_id).click()

    # 業種詳細をセット
    # くっそ長いので勘弁してほしい
    _ids = [
        'industryInfoArray_1[v_9000]', 'industryInfoArray_1[v_15000]', 'industryInfoArray_1[v_13000]', 'industryInfoArray_1[v_13500]', 'industryInfoArray_1[v_13600]', 'industryInfoArray_1[v_89620]', 'industryInfoArray_1[v_14000]', 'industryInfoArray_1[v_14200]', 'industryInfoArray_1[v_14500]', 'industryInfoArray_1[v_39300]', 'industryInfoArray_1[v_28000]', 'industryInfoArray_1[v_16000]', 'industryInfoArray_1[v_17000]', 'industryInfoArray_1[v_20000]', 'industryInfoArray_1[v_23000]', 'industryInfoArray_1[v_21000]', 'industryInfoArray_1[v_22000]', 'industryInfoArray_1[v_24000]', 'industryInfoArray_1[v_26000]', 'industryInfoArray_1[v_27000]', 'industryInfoArray_1[v_12200]', 'industryInfoArray_1[v_30000]', 'industryInfoArray_1[v_31000]', 'industryInfoArray_1[v_32000]', 'industryInfoArray_1[v_33000]', 'industryInfoArray_1[v_39700]', 'industryInfoArray_1[v_34000]', 'industryInfoArray_1[v_34500]', 'industryInfoArray_1[v_36000]', 'industryInfoArray_1[v_33100]', 'industryInfoArray_1[v_37000]', 'industryInfoArray_1[v_37300]', 'industryInfoArray_1[v_38000]', 'industryInfoArray_1[v_38500]', 'industryInfoArray_1[v_38600]', 'industryInfoArray_1[v_37400]', 'industryInfoArray_1[v_38700]', 'industryInfoArray_1[v_39500]', 'industryInfoArray_1[v_89650]', 'industryInfoArray_2[v_41000]', 'industryInfoArray_2[v_41400]', 'industryInfoArray_2[v_41500]', 'industryInfoArray_2[v_42000]', 'industryInfoArray_2[v_42100]', 'industryInfoArray_2[v_44000]', 'industryInfoArray_2[v_45000]', 'industryInfoArray_2[v_46100]', 'industryInfoArray_2[v_46200]', 'industryInfoArray_2[v_48300]', 'industryInfoArray_2[v_49100]', 'industryInfoArray_2[v_50000]', 'industryInfoArray_2[v_52000]', 'industryInfoArray_2[v_49200]', 'industryInfoArray_2[v_49300]', 'industryInfoArray_2[v_49400]', 'industryInfoArray_2[v_51000]', 'industryInfoArray_2[v_51500]', 'industryInfoArray_2[v_52500]', 'industryInfoArray_2[v_53600]', 'industryInfoArray_2[v_54000]', 'industryInfoArray_2[v_53000]', 'industryInfoArray_2[v_57500]', 'industryInfoArray_3[v_55000]', 'industryInfoArray_3[v_56000]', 'industryInfoArray_3[v_56100]', 'industryInfoArray_3[v_56500]', 'industryInfoArray_3[v_57000]', 'industryInfoArray_3[v_56300]', 'industryInfoArray_3[v_58000]', 'industryInfoArray_3[v_58010]', 'industryInfoArray_3[v_58015]', 'industryInfoArray_3[v_58020]', 'industryInfoArray_3[v_58040]', 'industryInfoArray_3[v_58060]', 'industryInfoArray_3[v_58070]', 'industryInfoArray_3[v_58080]', 'industryInfoArray_3[v_58050]', 'industryInfoArray_4[v_60000]', 'industryInfoArray_4[v_61050]', 'industryInfoArray_4[v_61100]', 'industryInfoArray_4[v_61300]', 'industryInfoArray_4[v_61500]', 'industryInfoArray_4[v_62000]', 'industryInfoArray_4[v_72000]', 'industryInfoArray_4[v_64100]', 'industryInfoArray_4[v_74500]', 'industryInfoArray_4[v_70000]', 'industryInfoArray_4[v_65100]', 'industryInfoArray_4[v_71000]', 'industryInfoArray_4[v_68000]', 'industryInfoArray_4[v_75000]', 'industryInfoArray_4[v_66000]', 'industryInfoArray_4[v_73000]', 'industryInfoArray_4[v_74000]', 'industryInfoArray_5[v_80000]', 'industryInfoArray_5[v_80200]', 'industryInfoArray_5[v_86000]', 'industryInfoArray_5[v_86500]', 'industryInfoArray_5[v_87000]', 'industryInfoArray_5[v_87150]', 'industryInfoArray_5[v_87300]', 'industryInfoArray_5[v_88300]', 'industryInfoArray_5[v_87100]', 'industryInfoArray_5[v_88500]', 'industryInfoArray_5[v_88200]', 'industryInfoArray_5[v_80100]', 'industryInfoArray_5[v_87200]', 'industryInfoArray_5[v_87900]', 'industryInfoArray_5[v_96420]', 'industryInfoArray_5[v_96450]', 'industryInfoArray_5[v_96470]', 'industryInfoArray_5[v_96490]', 'industryInfoArray_5[v_96500]', 'industryInfoArray_5[v_88000]', 'industryInfoArray_5[v_89500]', 'industryInfoArray_5[v_89600]', 'industryInfoArray_5[v_96430]', 'industryInfoArray_5[v_89700]', 'industryInfoArray_7[v_95000]', 'industryInfoArray_7[v_95100]', 'industryInfoArray_7[v_95200]', 'industryInfoArray_7[v_96410]', 'industryInfoArray_5[v_82000]',
    ]

    for _id in _ids:
        js = f'document.getElementById("{_id}").checked = true;'
        driver.execute_script(js)

    # 戻ってくる
    js = 'javascript:searchIndustry("displayCorpSearchByGenCondForm","/22/pc/corpinfo/displayCorpSearchByGenCond/doSearchIndustry");return false;'
    driver.execute_script(js)

    # 人数設定
    for i in range(2, 7):
        js = f'document.getElementById("crpNumOfEmployeesCtgDispListCheck{i}").checked = true;'
        driver.execute_script(js)

    _id = 'srchNarrowDownButton'
    driver.find_element_by_id(_id).click()

    # URL取得
    url_list = []

    _id = 'searchResultkensuu'
    all_count = int(driver.find_element_by_id(_id).text)

    # すぐ使うやつを定義
    cnt = 0
    multiple = [i for i in range(1, all_count) if i % 100 == 0]

    for i in tqdm(range(0, all_count)):
        if i in multiple or cnt == 100:
            js = f'javascript:calcNextPage("displaySearchCorpListByGenCondDispForm", "{i}", "100"); setActionMode("displaySearchCorpListByGenCondDispForm", "/22/pc/corpinfo/searchCorpListByGenCond/doNextPage");return false;'
            driver.execute_script(js)
            cnt = 0
        _id = f'corpNameLink[{cnt}]'
        try:
            el = driver.find_element_by_id(_id)
        except:
            return url_list
        url_list.append(el.get_attribute('href'))
        cnt += 1

    return url_list


def kyuujinhyou(URL):
    XPATHS = {
        '抽出元': '',
        '企業名': '//*[@id="companyHead"]/div[1]/div/div/div[1]/h1',
        '住所': '//*[@id="corpDescDtoListDescText50"]',
        '電話番号': '//*[@id="corpDescDtoListDescText220"]',
        'URL': '//*[@id="corpDescDtoListDescText120"]/text()',
    }

    # # torでスクレイピング
    # options = ChromeOptions()
    # options.add_argument('--headless')
    # driver = Chrome(options=options)

    while True:
        try:
            req = requests.get(URL)
            break
        except:
            pass

    soup = BeautifulSoup(req.text, 'html.parser')
    lxml = html.fromstring(str(soup))
    texts = []
    for key in XPATHS:
        xpath = XPATHS[key]
        if key == '抽出元':
            text = 'マイナビ50名-100名'
        elif key == 'URL':
            url_hp = get_str_from_xpath(xpath, lxml)
            if url_hp is None:
                text = URL
            else:
                pat = 'https?://[\w!?/+\-_~;.,*&@#$%()\'[\]]+'
                res = re.search(pat, url_hp)
                if res is None:
                    text = URL
                else:
                    text = res.group()
        else:
            text = get_str_from_xpath(xpath, lxml)
        texts.append(text)

    return texts


def main():

    urls = get_url()
    with open('mynavi_urls.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(urls)

    with open('mynavi_urls.csv') as f:
        urls = [x[0] for x in csv.reader(f)]

    texts = []

    # # テスト用
    # for url in tqdm(urls):
    #     res = kyuujinhyou(url)
    #     texts.append(res)

    # 本番用
    pool = Pool(processes=20)
    with tqdm(total=len(urls)) as t:
        for res in pool.imap_unordered(kyuujinhyou, urls):
            texts.append(res)
            t.update(1)

    write_csv(texts, 'mynavi_datas.csv')


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
        return None
    else:
        try:
            return el[0].text
        except AttributeError:
            # text()用
            return str(el[0])


if __name__ == "__main__":
    main()
