import mailhandler
import sys
import time
import os
from const import Base
from log import log, err_log
from pprint import pprint
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from log import SimpleLog as sl
from crawler_utils import (
    AD_YEAR,
    LAMBDA_DICT,
    YEAR,
    datetime_maker,
    find_kw,
    get_html_element,
    get_web_driver,
    read_all_pdf,
)
from request_info_creator import (
    AgrstatOfficialInfoCreator as agroff,
    ForestCreator as fc,
    SwcbCreator as sc,
    InquireAdvanceCreator as ia,
    WoodPriceCreator as wc,
    AgrstatBookCreator as abc,
    ApisAfaCreator as aac,
    PirceNaifCreator as pnc,
    BliCreator as bc,
    PxwebCreator as pc,
    AgrCostCreator as acc,
    FishYearCreator as fyc,
)

kws_d = {}
kws_l = []
forest_kws_l = []
fish_year_l = []


def start_crawler(key, url) -> None:
    """
    找到對應網址的 fn
    :param key:關鍵字
    :param url: 要解析的網址
    :return: None
    """

    # if url.find('OfficialInformation') != -1:
    #     extract_agrstat_official_info(key, url)
    #
    # elif url.find('swcb') != -1:
    #     extract_swcb(key, url)
    #
    # if url.find('0000575') != -1:
    #     extract_forest(key, url)
    #
    # elif url.find('InquireAdvance') != -1:
    #     extract_inquire_advance(key, url)
    #
    # elif url.find('woodprice') != -1:
    #     extract_wood_price(key, url)
    #
    # elif url.find('book') != -1:
    #     extract_agrstat_book(key, url)
    #
    # if url.find('apis.afa.gov.tw') != -1:
    #     extract_apis_afa(key, url)
    #
    # if url.find('price.naif.org.tw') != -1:
    #     extract_price_naif(key, url)
    # #
    # elif url.find('www.bli.gov.tw') != -1:
    #     extract_bli(key, url)
    #
    # elif url.find('210.69.71.166') != -1:
    #     extract_pxweb(key, url)

    # if url.find('itemNo=COI121') != -1:
    #     extract_agrcost(key, url)

    if url.find('FishYear') != -1:
        extract_fish_year(key, url)


def extract_agrstat_official_info(key, url) -> None:
    """
    將關鍵字與網址傳進來，一次創建所有關鍵字的列表，
    將網頁解析後取出網頁的關鍵字跟關鍵字列表比對，若存在就刪除直到關鍵字列表個數為零
    同時判斷若以解析到最後一頁要結束迴圈
    :param key: 關鍵字
    :param url: 網址，解析用
    :return: None
    """
    kws_d[key] = ''
    if len(kws_d) == agroff.len():
        creator = agroff()
        driver = get_web_driver()
        driver.get(url)
        while True:
            if len(kws_d) == 0:
                driver.quit()
                break

            try:
                element, soup = get_html_element(agroff.tag('tr_row1'), agroff.tag('tr_row2'),
                                                 page_source=driver.page_source, return_soup=True)
                kw_list = LAMBDA_DICT['kw_list'](element)
                for k in kw_list:
                    if k in kws_d.keys():
                        log.info('find ', k, ' at page ', creator.page, unpacking=False)
                        del kws_d[k]

                # 取得最後一個 td tag 的文字，用來判斷是否為最後一頁或者是更多頁面
                flag = LAMBDA_DICT['specified_element_text'](soup(agroff.tag('td')), -1)
                if flag == '...':
                    if creator.page.endswith('0'):
                        driver.find_element_by_xpath(creator.tag('more_page')).click()
                        creator.page = 1
                        continue
                else:
                    if creator.page == flag:
                        driver.quit()
                        if len(kws_d) != 0:
                            err_log.warning('not found keyword: ', kws_d.keys(), unpacking=False)
                        print('Page end, ', creator.page, 'pages')
                        break

                creator.page = 1
                driver.find_element_by_xpath(creator.tag('page').format(creator.page)).click()
                driver.implicitly_wait(3)
            except Exception:
                driver.quit()
                t, v, tr = sys.exc_info()
                err_log.error('error occurred.\t', t, '\t', v)
                break


def extract_swcb(key, url) -> None:
    """
    將關鍵字與網址傳進來，一次創建所有關鍵字的列表，
    將網頁解析後取出網頁的關鍵字跟關鍵字列表比對，若存在則將 key 與 url 加到字典裡
    並迭代開啟 excel 確認年度是否正確
    :param key: 關鍵字
    :param url: 網址，解析用
    :return: None
    """
    kws_l.append(key)
    if len(kws_l) == sc.len:
        creator = sc()
        k_f_l_d = {}
        element, soup = get_html_element(sc.tag('h3'), method='get', return_soup=True, url=url, creator=creator)
        # 頁面上的關鍵字
        kw = LAMBDA_DICT['kw_list'](element)
        # 連結網址
        file_link = LAMBDA_DICT['file_link_list']('/'.join(url.split('/')[:-1]) + '/{}', soup(sc.tag('a')))
        # 頁面關鍵字如果有在列表裡，則加到字典裡
        for w, f in zip(kw, file_link):
            if any((w.find(i) != -1) for i in kws_l):
                k_f_l_d[w] = f

        # 迭代搜尋關鍵字
        for k, v in k_f_l_d.items():
            flag_year, datetime_start, datetime_end = datetime_maker(spec=sc.day)
            format_keyword = sc.kw.format(flag_year-1)
            find, text = find_kw(v, format_keyword)
            if find:
                log.info(format_keyword, k, text)
            else:
                if text < format_keyword:
                    mailhandler.set_msg(False, k, url, format_keyword)
                else:
                    mailhandler.set_msg(True, k, url, format_keyword, text)
                err_log.warning(format_keyword, k, text)


def extract_forest(key, url) -> None:
    forest_kws_l.append(key)
    if len(forest_kws_l) == fc.len():
        creator = fc()
        k_f_l_d = {}
        element, soup = get_html_element(fc.tag('td_of_1'), method='get',
                                         return_soup=True, url=url, creator=creator)
        kw = LAMBDA_DICT['kw_list'](element)
        file_link = LAMBDA_DICT['file_link_list']('/'.join(url.split('/')[:-1]) + '{}', soup(fc.tag('a')))

        for w, f in zip(kw, file_link):
            if any((w.find(i) != -1) for i in forest_kws_l):
                k_f_l_d[w] = f

        for k, v in k_f_l_d.items():
            print(v)
            if k == '造林面積':
                now = time.strftime('%m%d%H%M')
                keyword = '{}年第{}季'
                month = ['', '01311700', '', '', '04301700', '', '', '07311700', '', '', '10311700']
                if month[1] < now <= month[4]:
                    format_keyword = keyword.format(YEAR, 4)
                    datetime_start = month[1]
                    datetime_end = month[4]
                elif month[4] < now <= month[7]:
                    format_keyword = keyword.format(YEAR, 1)
                    datetime_start = month[4]
                    datetime_end = month[7]
                elif month[7] < now <= month[10]:
                    format_keyword = keyword.format(YEAR, 2)
                    datetime_start = month[7]
                    datetime_end = month[10]
                else:
                    format_keyword = keyword.format(YEAR, 3)
                    datetime_start = month[10]
                    datetime_end = month[1]
                sl.set_msg(datetime_start, datetime_end)

                find, text = find_kw(v, format_keyword, 'ods')
                if find:
                    log.info(format_keyword, k, text)
                else:
                    mailhandler.set_msg(False, k, url, format_keyword)
                    err_log.warning(format_keyword, k, text)

            elif k == '林務局森林遊樂區收入' or k == '木材市價':
                flag_month, datetime_start, datetime_end = datetime_maker(day=creator.days)
                if k == '林務局森林遊樂區收入':
                    format_keyword = creator.income_date.format(YEAR, int(flag_month)-1)
                    find, text = find_kw(v, format_keyword, 'ods')
                else:
                    format_keyword = creator.wood_date.format(YEAR, int(flag_month)-1)
                    find, text = find_kw(v, format_keyword, 'stream')

                if find:
                    log.info(format_keyword, k, text)
                else:
                    if k == '林務局森林遊樂區收入':
                        text = text.split(':')[1]
                    else:
                        text = text[1:text.index('份')]
                    if text < format_keyword:
                        mailhandler.set_msg(False, k, url, format_keyword)
                    else:
                        mailhandler.set_msg(True, k, url, format_keyword, text)
                    err_log.warning(format_keyword, key, text)


def extract_inquire_advance(key, url) -> None:
    """
    如果 key == 老農津貼相關, 月份為當月的前兩個月, 其他則為前一個月
    last_two_tr: 因最新的月份為倒數第二個 tr 元素, 因此可用來判斷是否未在指定時間內更新資料
    :param key: 農民生產所得物價指數, 農民生產所付物價指數, 老年農民福利津貼核付人數, 老年農民福利津貼核付金額
    :param url: http://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    :return: None
    """
    creator = ia(key)

    if key in ['老年農民福利津貼核付人數', '老年農民福利津貼核付金額', '農業生產結構']:
        flag_year, datetime_start, datetime_end = datetime_maker(spec=creator.spec_day)
        keyword = str(flag_year-1)+'年'
    else:
        flag_month, datetime_start, datetime_end = datetime_maker(day=ia.days)
        keyword = ia.kw.format(int(flag_month)-1)
    element = get_html_element(ia.tag('tr'), url=url, creator=creator)
    text = LAMBDA_DICT['specified_element_text'](element, -2)
    if text.find(keyword) != -1:
        log.info(keyword, key, text)
    else:
        mailhandler.set_msg(False, key, url, keyword)
        err_log.warning(keyword, key, text)


def extract_wood_price(key, url) -> None:
    """
    爬取 木材市價 website
    :param key: 木材市價
    :param url: https://woodprice.forest.gov.tw/Compare/Q_CompareProvinceConiferous.aspx
    :return: None
    """
    creator = wc()
    flag_month, datetime_start, datetime_end = datetime_maker(day=wc.days)

    # 確認前一個月、當月、下個月是否有資料
    for i in range(1, -2, -1):
        creator.set_years(YEAR)
        creator.set_months(int(flag_month) - i)
        format_keyword = wc.kw.format(YEAR, int(flag_month) - i)
        element = get_html_element(wc.tag('tr_of_2'), url=url, creator=creator)
        text = LAMBDA_DICT['specified_element_text'](element, 0)
        if i == 1:
            if text.find(format_keyword) != -1:
                log.info(format_keyword, key, text)
            else:
                mailhandler.set_msg(False, key, url, format_keyword, text)
                err_log.warning(format_keyword, key, text)
        else:
            if text.find(format_keyword) != -1:
                kw = wc.kw.format(YEAR, int(flag_month)-1)
                sl.set_msg(datetime_start, datetime_end)
                mailhandler.set_msg(True, key, url, kw, text)
                err_log.warning(kw, key, text)


def extract_agrstat_book(key, url) -> None:
    if key in ['糧食供需統計', '農作物種植面積、產量', '畜牧用地面積',
               '畜產品生產成本', '毛豬飼養頭數', '農業及農食鏈統計', '畜禽飼養及屠宰頭（隻）數', '畜禽產品生產量值']:
        creator = abc(key)
        element = get_html_element(creator.tag, return_soup=False, url=url, creator=creator)
        file_link = LAMBDA_DICT['specified_file_link_slice']('/'.join(url.split('/')[:-1]) + '/', element, 0)
        if key == '毛豬飼養頭數':
            now = time.strftime('%m%d%H%M')
            jan = str(YEAR)+'01151700'
            jul = str(YEAR)+'07161700'
            datetime_start = jul if jul < str(YEAR)+now else jan
            datetime_end = str(YEAR+1)+'01151700' if jul < str(YEAR)+now else jul
            sl.set_msg(datetime_start, datetime_end)
            format_keyword = abc.date.format(YEAR, 5) if datetime_start == jul else \
                abc.date.format(YEAR-1, 11)
            find, text = find_kw(file_link, format_keyword, file_type='pdf')
            if find:
                log.info(format_keyword, key, text)
            else:
                if text < format_keyword:
                    mailhandler.set_msg(False, url, key, format_keyword)
                else:
                    mailhandler.set_msg(True, url, key, format_keyword, text)
                err_log.warning(format_keyword, key, text)

        else:
            flag_year, datetime_start, datetime_end = datetime_maker(spec=creator.day)
            format_keyword = abc.kw.format(flag_year-1)
            if key == '農業及農食鏈統計':
                find, text = find_kw(file_link, format_keyword, file_type='ods')
            else:
                find, text = find_kw(file_link, format_keyword, file_type='pdf')
            if find:
                log.info(format_keyword, key, text)
            else:
                if int(text[text.index('1'):text.index('年')]) < flag_year-1:
                    mailhandler.set_msg(False, url, key, str(flag_year-1)+'年')
                else:
                    mailhandler.set_msg(True, url, key, str(flag_year - 1)+'年', text[:text.index('年')+1])
                err_log.warning(format_keyword, key, text)


def extract_apis_afa(key, url) -> None:
    flag_month, datetime_start, datetime_end = datetime_maker(day=aac.days)
    format_keyword = aac.kw.format(AD_YEAR, int(flag_month)-1)
    driver = get_web_driver()
    try:
        driver.get(url)

        # 選擇開始月份
        Select(driver.find_element_by_id(aac.tag('month_start'))).select_by_value('1')

        # 選擇結束月份
        Select(driver.find_element_by_id(aac.tag('month_end'))).select_by_value('12')

        # 選擇指定品項(葡萄)
        driver.find_element_by_id(aac.tag('check_box_grape')).click()

        # 按下搜尋
        driver.find_element_by_class_name(aac.tag('search_button')).click()

        # 等到 time out(5s)
        WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) == 2)

        # 切換到跳出的頁面
        driver.switch_to_window(driver.window_handles[1])
        element = get_html_element(aac.tag('tr'), page_source=driver.page_source)
        texts = LAMBDA_DICT['kw_list'](element)

        # 判斷是否為 當月-1 的月份資料
        if texts[int(flag_month)-1].find('-') == -1:
            log.info(format_keyword, key, texts[int(flag_month)-1])
        else:
            mailhandler.set_msg(False, key, url, str(texts[int(flag_month)-1])+'月')
            err_log.warning(format_keyword, key, texts[int(flag_month)-1])

        # 判斷是否偷跑(是否為 當月 資料)
        if texts[int(flag_month)].find('-') == -1:
            mailhandler.set_msg(True, key, url, str(texts[int(flag_month)-1])+'月', str(texts[int(flag_month)])+'月')
            err_log.warning(format_keyword, key, texts[int(flag_month)])
    finally:
        driver.quit()


def extract_price_naif(key, url):
    flag_month, datetime_start, datetime_end = datetime_maker(day=pnc.days)
    creator = pnc()
    element = get_html_element(pnc.tag('option'), method='get', url=url, creator=creator)
    value = LAMBDA_DICT['specified_element_text'](element, 0)
    if int(value) == int(flag_month)-1:
        log.info(str(int(flag_month)-1)+'月', key, value)
    else:
        mailhandler.set_msg(False, key, url, str(int(flag_month)-1)+'月')
        err_log.warning(str(int(flag_month)-1)+'月', key, value)


def extract_bli(key, url):
    flag_month, datetime_start, datetime_end = datetime_maker(day=bc.days)
    creator = bc()
    format_keyword = bc.kw.format(YEAR, int(flag_month)-2)
    format_url = bc.url.format(str(int(flag_month)-2).rjust(2, '0'))
    element = get_html_element(bc.tag('a'), method='get', url=format_url, creator=creator)
    if not element:
        mailhandler.set_msg(False, key, url, format_keyword)
        err_log.warning(format_keyword, key, 'not found.')
    else:
        file_link = LAMBDA_DICT['specified_file_link']('/'.join(url.split('/')[0:3])+'/', element, 0)
        find, text = find_kw(file_link, format_keyword, file_type='csv')
        if find:
            log.info(format_keyword, key, text)
        else:
            if text[4:] < format_keyword:
                mailhandler.set_msg(False, key, url, format_keyword)
            else:
                mailhandler.set_msg(True, key, url, format_keyword, text)
            err_log.warning(format_keyword, key, text)


def extract_pxweb(key, url):
    flag_year, datetime_start, datetime_end = datetime_maker(spec=pc.day)
    format_keyword = pc.kw.format(flag_year-1)
    driver = get_web_driver()
    try:
        driver.get(pc.url)

        # 總戶口 or 農家戶口
        Select(driver.find_element_by_name('values1')).select_by_value('2')

        # 全選 or 不全選
        driver.find_element_by_xpath(pc.tag('all')).click()

        # 台北市
        Select(driver.find_element_by_name('values3')).select_by_value('3')

        # 確認送出
        driver.find_element_by_name('sel').click()
        driver.implicitly_wait(5)
        element = get_html_element('td.stub2', page_source=driver.page_source)
        texts = LAMBDA_DICT['kw_list'](element)[-2:]

        # make translate table
        table = str.maketrans(texts[0][:4], ' {}'.format(flag_year-2))
        if all(i.translate(table).strip().find(format_keyword) != -1 for i in texts):
            log.info(format_keyword, key, texts[0]+', '+texts[1])
        else:
            mailhandler.set_msg(False, key, url, format_keyword)
            err_log.warning(format_keyword, key, texts[0]+', '+texts[1])
    finally:
        driver.quit()


def extract_agrcost(key, url):
    if not os.path.isdir(Base.TEMP_PATH):
        os.mkdir(Base.TEMP_PATH)

    creator = acc()
    date_tuple = datetime_maker(spec=creator.day)
    keyword = creator.kw.format(date_tuple[0] - 1)
    read_all_pdf(Base.TEMP_PATH, key, keyword, date_tuple)
    browser = get_web_driver(dl_permission=True)
    try:
        browser.get(url)
        Select(browser.find_element_by_name(creator.tag('year'))).select_by_value(str(AD_YEAR - 1))

        for name in creator.item:
            Select(browser.find_element_by_id(creator.tag('item'))).select_by_value(name)
            browser.find_element_by_class_name(creator.tag('submit')).click()

            # in staleness_of fn is check by element.is_enabled()
            # use invisibility_of_element_located no effect because arg is locator
            WebDriverWait(browser, 5).until(ec.staleness_of(browser.find_element_by_class_name('blockUI')))

            i = 1
            flag = True
            while flag:
                element, soup = get_html_element(creator.tag('a'), page_source=browser.page_source, return_soup=True)
                file_link = LAMBDA_DICT['file_link_list']('{}', element)
                element = soup(creator.tag('td3'))[1:]
                name = LAMBDA_DICT['kw_list'](element)

                for z in zip(name, file_link):
                    print(z[0])
                    browser.execute_script(z[1])
                    WebDriverWait(browser, 5).until(ec.staleness_of(browser.find_element_by_class_name('blockUI')))

                present = ec.visibility_of_all_elements_located((By.CLASS_NAME, 'dxpCtrl'))
                if present(browser):
                    i += 1
                    if i > 2:
                        break
                    browser.find_element_by_xpath(creator.tag('td9')).click()
                    WebDriverWait(browser, 5).until(ec.staleness_of(browser.find_element_by_class_name('blockUI')))
                else:
                    flag = False
    finally:
        time.sleep(2)
        browser.quit()


def extract_fish_year(key, url):
    fish_year_l.append(key)
    if len(fish_year_l) == fyc.len():
        creator = fyc()
        flag_year, datetime_start, datetime_end = datetime_maker(spec=creator.day)
        element = get_html_element(creator.tag('a'), method='get', creator=creator, url=url)
        text = LAMBDA_DICT['kw_list'](element)[0]
        keyword = creator.kw.format(flag_year - 1)

        if text.find(keyword) != -1:
            log.info(keyword, '漁業統計年報', text)
        else:
            if keyword < text[:7]:
                mailhandler.set_msg(True, url, key, str(flag_year) + '年')
            else:
                mailhandler.set_msg(False, url, key, str(flag_year - 1) + '年')
            err_log.warning(keyword, '漁業統計年報', text)
