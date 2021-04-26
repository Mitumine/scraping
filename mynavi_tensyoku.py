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
import math


def main():
    get = Get()

    # ヒット数取得
    hits = int(get.hits())

    # # 切り上げ
    # page_num_max = math.ceil(hits / 50)
    # hit_page_nums = range(1, page_num_max)

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

    # with open('mynavi_urls.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(child_urls)

    # 情報取得
    with open('mynavi_urls.csv') as f:
        urls = [x[0] for x in csv.reader(f)]

    # 本番用
    texts = []
    pool = Pool(processes=10)
    with tqdm(total=len(urls)) as t:
        for res in pool.imap_unordered(get.page_data, urls):
            texts.append(res)
            t.update(1)

    with open('mynavi_datas.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(texts)


class Get:
    URL_PARTS_FRONT = 'https://tenshoku.mynavi.jp'

    def page_data(self, url):
        xpath = '//*[@class="companyName"]'
        lxml = self.lxml(url)
        return self.str_from_xpath(xpath, lxml)

    def href(self, num: int):
        '''
        ページ内50件を片っ端から捜査する
        '''
        url = f'https://tenshoku.mynavi.jp/list/pa1_pa2/pg{num}/?jobsearchType=4&searchType=8'
        lxml = self.lxml(url)

        child_urls = []
        for i in range(1, 50):
            xpath = f'/html/body/div[1]/div[3]/form/div/div[{i}]/div/section/p/a/@href'
            url_parts = self.str_from_xpath(xpath, lxml)
            if url_parts is None:
                continue
            url = self.URL_PARTS_FRONT + url_parts
            child_urls.append(url)

        return child_urls

    def hits(self):
        '''
        何件ヒットしたか？
        '''

        URL_PARTS_BEHIND = '/list/pa1_pa2/?jobsearchType=4&searchType=8'
        url = self.URL_PARTS_FRONT + URL_PARTS_BEHIND

        lxml = self.lxml(url)
        XPATH = '/html/body/div[1]/div[3]/div[2]/div/p[2]/em'

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
                pass

        soup = BeautifulSoup(req.text, 'html.parser')
        lxml = html.fromstring(str(soup))
        return lxml

    def str_from_xpath(self, xpath: str, lxml):
        '''
        lxmlの情報をもとに、Xpathが内包する「テキスト」をreturn
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
