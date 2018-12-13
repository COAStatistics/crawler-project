from bs4 import BeautifulSoup as bs
from datetime import date
from log import SimpleLog as sl
from log import log, err_log
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from selenium import webdriver
import codecs
import csv
import io
import os
import pyexcel_ods
import requests
import shelve
import time
import xlrd
from const import Base
from pdfminer.pdfinterp import (
    PDFPageInterpreter,
    PDFResourceManager,
    PDFDocument,
    PDFParser
)

AD_YEAR = date.today().year
# 西元轉民國年
YEAR = AD_YEAR - 1911
# switch-like
LAMBDA_DICT = {
    'kw_list': lambda l: [i.get_text().strip().replace(' ', '') for i in l],
    'file_link_list': lambda url, l: [url.format(i.get('href')) for i in l],
    'specified_element_text': lambda l, x: l[x].get_text().strip().replace(' ', ''),
    'specified_file_link_slice': lambda url, l, x: str(url + l[x].get('href').split('/')[1]),
    'specified_file_link': lambda url, l, x: str(url + l[x].get('href')),
}

req = requests.Session()


def get_html_element(*args, method='post', page_source=None, return_soup=False, **kwargs):
    """
    get html element.
    :param args: str, soup selector, 但可能不只取得一個元素
    :param method: post or get
    :param page_source: if use selenium, pass driver.page_source
    :param return_soup: bool, if True, 代表要回傳 soup (reuse)
    :param kwargs: url and creator
    :return: list or tuple
    """
    element_list = []

    if page_source is not None:
        content = page_source
    else:
        creator = kwargs['creator']
        if method != 'post':
            content = req.get(kwargs['url'], headers=creator.headers).text
        else:
            content = req.post(kwargs['url'], headers=creator.headers, data=creator.form_data).content

    soup = bs(content, 'lxml')
    for i in args:
        element_list.extend(soup.select(i))
    if return_soup:
        return element_list, lambda x: soup.select(x)
    else:
        return element_list


def read_all_pdf(path, key, kw, date_tuple):
    with shelve.open('../mapping') as f:
        mapping = f['mapping']

    for index, file in enumerate(os.listdir(path)):
        if file.endswith('.crdownload'):
            continue
        if index > 0:
            sl.set_msg(date_tuple[1], date_tuple[2])

        pdf = open(path + '/' + file, 'rb')
        find, text = find_kw(pdf, kw, file_type='pdf', parse=True)

        if find:
            log.info(kw, key, mapping[file] + '-' + text)
        else:
            err_log.warning(kw, key, mapping[file] + '-' + text)


def find_kw(link, keyword, file_type='excel', parse=False) -> tuple:
    """
    judge the file type then inspection year
    :param link: files url
    :param keyword: keyword select
    :param file_type: csv, excel, ods, pdf
    :param parse: PDF file or IO stream ?
    :return: tuple
    """
    text = ''
    if file_type == 'ods':
        calc = pyexcel_ods.get_data(io.BytesIO(req.get(link).content))
        for sheet in list(calc.values()):
            for row in sheet:
                for cell in row:
                    cell_text = str(cell).strip().replace(' ', '')
                    if any(cell_text.find(i) != -1 for i in ['時期', '月份', '民國']):
                        text = cell_text
                        if keyword in text:
                            return True, text
        return False, text

    elif file_type == 'csv':
        rows = csv.reader(io.BytesIO(req.get(link).content).read().decode('big5'))
        for i in rows:
            for j in i:
                s = str(j).strip().replace('\u3000', '').replace(' ', '')
                if any(s.find(i) != -1 for i in ['中華民國']):
                    text = s
                    if keyword in text:
                        return True, text
                    else:
                        return False, text

    elif file_type == 'pdf':
        if parse:
            parser = PDFParser(link)
        else:
            parser = PDFParser(io.BytesIO(req.get(link).content))

        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize()
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        text = ''
        for index, page in enumerate(list(doc.get_pages())):
            if keyword.find('月底') != -1 and index == 1:
                break
            interpreter.process_page(page)
            layout = device.get_result()
            for o in layout:
                if isinstance(o, LTTextBoxHorizontal):
                    pdf_text = o.get_text().strip()
                    if any(pdf_text.find(i) != -1 for i in ['時期', '年', '年期']):
                        text = pdf_text.split(' ')[-1]
                    if text.find(keyword) != -1:
                        return True, text
        return False, text

    elif file_type == 'stream':
        reader = codecs.getdecoder('utf8')(bytes(req.get(link).content))[0]
        text = reader[reader.index('('):reader.index(')')].strip('()')
        if text.find(keyword) != -1:
            return True, text
        else:
            return False, text

    wb = xlrd.open_workbook(file_contents=requests.get(link).content)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            value = str(sheet.row_values(i)[j]).strip().replace(' ', '')
            if value.find('中華民國') != -1:
                text = value
                if keyword in value:
                    return True, text
    return False, text


def datetime_maker(day=None, spec=None) -> tuple:
    """
    產生發布日期的期間 ex: X月X日 - X月X日
    :param day: every month's release day
    :param spec: specified day
    :return: tuple
    now: 當下時間
    flag month: 是當月還是上個月份, 若為個位數月份前面須補 0
    datetime_start: release date start
    datetime_end: release date end
    """
    now = time.strftime('%m%d%H%M')
    if day:
        dateline = '{}{}1700'
        month = str(date.today().month).rjust(2, '0')
        # 判斷 now 是否大於當月日期, if True month=this month else month=previous month
        # ex: 09251700 < 09121700 ? if True month=09 else month=08
        flag_month = month if dateline.format(month, day[int(month)]) < now else str(int(month) - 1).rjust(2, '0')
        next_flag_month = month if dateline.format(month, day[int(month)]) > now else str(int(month) + 1).rjust(2, '0')
        datetime_start = dateline.format(flag_month, str(day[int(flag_month)]).rjust(2, '0'))
        datetime_end = dateline.format(next_flag_month, str(day[int(next_flag_month)]).rjust(2, '0'))
        sl.set_msg(datetime_start, datetime_end)
        return flag_month, datetime_start, datetime_end
    else:
        dateline = spec
        flag_year = YEAR if dateline < now else YEAR-1
        datetime_start = str(flag_year) + dateline
        datetime_end = str(flag_year+1) + dateline
        sl.set_msg(datetime_start, datetime_end)
        return flag_year, datetime_start, datetime_end


def get_web_driver(dl_permission=False) -> webdriver:
    """
    設定 Chrome 參數並回傳
    :return: webdriver object
    """
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-images')
    option.add_argument('--disable-gpu')
    option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option)
    if dl_permission:
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {'behavior': 'allow', 'downloadPath': Base.TEMP_PATH}
        }
        driver.execute("send_command", params)
    return driver