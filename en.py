from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
from pprint import pprint
import requests
from lxml import html, etree
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import re
from multiprocessing import Pool
import math
import time
import codecs


def main():
    # インスタンス設定
    get = Get()

    # # ヒット数取得
    # hits = int(get.hits())

    # # 切り上げ
    # page_num_max = math.ceil(hits / 50)
    # hit_page_nums = range(1, page_num_max)
    # # hit_page_nums = range(1, 2)

    # child_urls = []

    # # テスト用
    # # for num in tqdm(hit_page_nums):
    # #     child_urls += get.href(num)

    # # 本番用
    # pool = Pool(processes=10)
    # with tqdm(total=len(hit_page_nums)) as t:
    #     for res in pool.imap_unordered(get.href, hit_page_nums):
    #         child_urls += res
    #         t.update(1)

    # with open('en_urls.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerows([[x] for x in child_urls])

    # # return

    # 情報取得
    with open('en_urls.csv') as f:
        urls = [x[0] for x in csv.reader(f)]

    texts = []

    # # テスト用
    for num in tqdm(urls):
        texts.append(get.page_data(num))
        time.sleep(2)

    # 本番用
    # pool = Pool(processes=10)
    # with tqdm(total=len(urls)) as t:
    #     for res in pool.imap_unordered(get.page_data, urls):
    #         texts.append(res)
    #         t.update(1)

    with open('en_datas.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(texts)


class Get:
    URL_PARTS_FRONT = 'https://employment.en-japan.com/'

    def page_data(self, url):
        XPATHS = {
            '抽出元': '',
            '企業名': '//*[@id="descCompanyName"]/div[2]/div[2]/span[1]',
            '住所': '',
            '電話番号': '',
            'URL': '',
            '従業員数': '',
        }

        PATS = {
            '抽出元': None,
            '企業名': None,
            '住所': '連絡先(\n|.)*(.{2,3}[都道府県].+)',
            '電話番号': '連絡先(\n|.)+(\d{2,3}-\d{1,4}-\d{4})',
            'URL': '企業ホームページ(\n|.)+(https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)',
            '従業員数': '従業員数(\n|.)+>(.+名)</td>(\n|.)',
        }

        lxml = self.lxml(url)
        texts = []

        for key in XPATHS:
            xpath = XPATHS[key]
            pat = PATS[key]
            if key == '抽出元':
                text = 'エン転職未経験'
            elif key == '企業名':
                text = self.str_from_xpath(xpath, lxml)
            else:
                text = self.xpath_repat(pat, lxml)

            texts.append(text)

        return texts

    def xpath_repat(self, arg_pat, lxml):
        page_html = etree.tostring(
            lxml,
            method='html',
            encoding='utf-8').decode('utf-8')
        # 邪魔なところをカット
        pat = '<head>(\n|.)*</head>'
        page_html = re.sub(pat, '', page_html)
        pat = '<!-- About Personal -->(\n|.)*<!--TagKnightManageTagEnd-->'
        page_html = re.sub(pat, '', page_html)
        res = re.search(arg_pat, page_html)
        if res is None:
            page_html = 'None'
        else:
            page_html = res.group(2)
            # 邪魔な文字除去
            pat = '(\s|\t|\n)'
            page_html = re.sub(pat, '', page_html)

        return page_html

    def href(self, num: int):
        '''
        ページ内50件を片っ端から捜査する
        '''
        url = self.URL_PARTS_FRONT + \
            f'search/search_list/?areaid=21_22_23_24&topicsid=101_102&aroute=2&pagenum={num}&arearoute=1'
        lxml = self.lxml(url)

        child_urls = []
        for i in range(1, 50):
            xpath = f'//div[2]/div[3]/div[2]/div[{i}]/div[2]/div/div[1]/a/@href'
            url_parts = self.str_from_xpath(xpath, lxml)
            if url_parts is None:
                continue
            pat = 'eng_'
            url_parts = re.sub(pat, '', url_parts)
            url = self.URL_PARTS_FRONT + url_parts
            child_urls.append(url)

        return child_urls

    def hits(self):
        '''
        何件ヒットしたか？
        '''

        URL_PARTS_BEHIND = 'search/search_list/?areaid=21_22_23_24&topicsid=101_102&aroute=2'
        url = self.URL_PARTS_FRONT + URL_PARTS_BEHIND

        lxml = self.lxml(url)
        XPATH = '//*[@id="jobSearchListNum"]/div[1]/em'

        return self.str_from_xpath(XPATH, lxml)

    def lxml(self, URL: str):
        '''
        URLにアクセスしてlxmlをreturn
        '''
        while True:
            try:
                req = requests.get(URL)
                break
            except:
                time.sleep(5)

        soup = BeautifulSoup(req.text, 'lxml')
        lxml = html.fromstring(str(soup))
        return lxml

    def str_from_xpath(self, xpath: str, lxml):
        '''
        lxmlの情報をもとに、Xpathが内包する情報をreturn
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


if __name__ == '__main__':
    main()
