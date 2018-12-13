from const import LongText


class BaseCreator:
    def __init__(self, extra_headers=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        }
        if extra_headers is not None:
            headers.update(extra_headers)

        self.__headers = headers

    @property
    def headers(self):
        return self.__headers


# 公務統計
class AgrstatOfficialInfoCreator(BaseCreator):
    __KEYWORDS_LENTH = 19
    __SELECT_DICT = {
        'tr_row1': 'tr.Row > td:nth-of-type(3)',
        'tr_row2': 'tr.AlternatingRow > td:nth-of-type(3)',
        'td': 'tr.Pager > td > table > tbody > tr > td',
        'more_page': '//tr[@class="Pager"]/td/table/tbody/tr/td[last()]/a[contains(text(), "...")]',
        'page': '//tr[@class="Pager"]/td/table/tbody/tr/td/a[contains(text(), {})]'
    }

    def __init__(self):
        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=pna0ob55eyuneo45wmltoi55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/official/OfficialInformation.aspx',

        }
        super().__init__(headers)

        self.__form_data = {
            '__EVENTTARGET': 'ctl00$cphMain$uctlOfficialInformation1$grdReport',
            '__EVENTARGUMENT': 'Page$1',
            '__VIEWSTATE': LongText.VIEWSTATE,
            '__VIEWSTATEGENERATOR': '36C3D52C',
            '__EVENTVALIDATION': LongText.EVENTVALIDATION,
            'ctl00$cphMain$uctlOfficialInformation1$ddlQYear': '',
            'ctl00$cphMain$uctlOfficialInformation1$ddlQPeriod': '',
            'ctl00$cphMain$uctlOfficialInformation1$txtQReportCode': '',
            'ctl00$cphMain$uctlOfficialInformation1$chkQNew': 'on',
            'ctl00$cphMain$uctlOfficialInformation1$txtQReportName': '',
            'ctl00$cphMain$uctlOfficialInformation1$ddlQOrganization': '0',
        }
        self.__page_index = 1

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]

    @staticmethod
    def len() -> int:
        return AgrstatOfficialInfoCreator.__KEYWORDS_LENTH

    @property
    def page(self) -> str:
        return str(self.__page_index)

    @page.setter
    def page(self, i):
        self.__page_index += i


class SwcbCreator(BaseCreator):
    __KEYWORDS_LENTH = 3
    __KEYWORD = '中華民國{}年度'
    __SPECIFIED_DAY = '05151700'
    __SELECT_DICT = {
        'h3': 'div.lastList > ul > li > a > h3',
        'a': 'div.lastList > ul > li > a',
    }

    @property
    def len(self) -> int:
        return self.__KEYWORDS_LENTH

    @property
    def kw(self) -> str:
        return self.__KEYWORD

    @property
    def day(self) -> str:
        return self.__SPECIFIED_DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class ForestCreator(BaseCreator):
    __KEYWORDS_LENTH = 7
    __KEYWORD = '中華民國{}年度'
    __INCOME_KEYWORD = '{}年{}月'
    __WOOD_KEYWORD = '{}年{}月'
    __DAY = ['', 25, 26, 26, 25, 25, 25, 25, 27, 25, 25, 26, 25]
    __SELECT_DICT = {
        'td_of_1': '#divContent > div.downloadBox > table > tbody > tr > td:nth-of-type(1)',
        'a': '#divContent > div.downloadBox > table > tbody > tr > td > a',
    }

    @staticmethod
    def len() -> int:
        return ForestCreator.__KEYWORDS_LENTH

    @property
    def kw(self) -> str:
        return self.__KEYWORD

    @property
    def income_date(self):
        return self.__INCOME_KEYWORD

    @property
    def wood_date(self):
        return self.__WOOD_KEYWORD

    @property
    def days(self) -> list:
        return self.__DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class InquireAdvanceCreator(BaseCreator):
    __KEYWORD = '{}月'
    __DAY = ['', 21, 20, 20, 22, 20, 20, 22, 20, 20, 22, 20, 20]
    __ELDER_DAY = ['', 22, 21, 20, 20, 21, 20, 20, 20, 20, 15, 15, 17]
    __SELECT_DICT = {
        'tr': '#ctl00_cphMain_uctlInquireAdvance_tabResult > tr',
    }

    def __init__(self, kw):
        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=wm50tvjgnavgxtienzqwlc55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx',

        }
        super().__init__(headers)

        self.__form_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': LongText.FARMER_INCOME_VIEWSTATE,
            '__VIEWSTATEGENERATOR': '20124335',
            '__EVENTVALIDATION': LongText.FARMER_INCOME_EVENTVALIDATION,
            'ctl00$cphMain$uctlInquireAdvance$lstFieldGroup': '3094',
            'ctl00$cphMain$uctlInquireAdvance$btnQuery': '查詢確認',
            '__LASTFOCUS': '',
        }
        if kw == '農民生產所付物價指數':
            self.__form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '3099'
            self.__form_data['__VIEWSTATE'] = LongText.FARMER_PAID_VIEWSTATE
            self.__form_data['__EVENTVALIDATION'] = LongText.FARMER_PAID_EVENTVALIDATION
        elif kw == '農業生產結構':
            self.spec_day = '07151700'
            self.__form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '3080'
            self.__form_data['__VIEWSTATE'] = LongText.AGRICULTURE_VIEWSTATE
            self.__form_data['__EVENTVALIDATION'] = LongText.AGRICULTURE_EVENTVALIDATION
        elif kw == '老年農民福利津貼核付人數':
            self.__form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '56'
            self.__form_data['__VIEWSTATE'] = LongText.ELDER_NOP_VIEWSTATE
            self.__form_data['__EVENTVALIDATION'] = LongText.ELDER_NOP_EVENTVALIDATION
        elif kw == '老年農民福利津貼核付金額':
            self.__form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '57'
            self.__form_data['__VIEWSTATE'] = LongText.ELDER_AMOUNT_VIEWSTATE
            self.__form_data['__EVENTVALIDATION'] = LongText.ELDER_AMOUNT_EVENTVALIDATION

    @property
    def days(self) -> list:
        return self.__DAY

    @property
    def kw(self) -> str:
        return self.__KEYWORD

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]

    def set_start_date(self, date):
        self.__form_data['ctl00$cphMain$uctlInquireAdvance$ddlMonthBegin'] = date

    def set_end_date(self, date):
        self.__form_data['ctl00$cphMain$uctlInquireAdvance$ddlMonthEnd'] = date


class WoodPriceCreator(BaseCreator):
    __KEYWORD = '{}年{}月'
    __DAY = ['', 25, 26, 26, 25, 25, 25, 25, 27, 25, 25, 26, 25]
    __SELECT_DICT = {
        'tr_of_2': '#ctl00_Main_q2_gv > tr:nth-of-type(2)',
    }

    def __init__(self):
        headers = {
            'Cookie': '_ga=GA1.3.1949248998.1534385798; __utmz=227712522.1534385798.1.1.utmcsr=(direct)|utmccn=(direct)'
                      '|utmcmd=(none); ASP.NET_SessionId=0kxdbqnbid0bupupgs3yzcch; _gid=GA1.3.1204522383.1537413421;'
                      ' __utma=227712522.1949248998.1534385798.1537171059.1537413421.9; __utmc=227712522;'
                      ' TS0172de76=01215f806c7a994aa6f5188886c7994a55f22d6852b26b1d578850315d8663591cf62af313275fddb2ba'
                      '1cfadc3e42d01316bfe778',
            'Origin': 'https://woodprice.forest.gov.tw',
            'Referer': 'https://woodprice.forest.gov.tw/Compare/Q_CompareProvinceConiferous.aspx',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        super().__init__(headers)
        self.form_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': LongText.WOOD_PRICE_VIEWSTATE,
            '__VIEWSTATEGENERATOR': 'F06CDE5E',
            'ctl00$Main$CompareQueryUi1$q1_ddl_years': '107',
            'ctl00$Main$CompareQueryUi1$q1_ddl_months': '9',
            'ctl00$Main$CompareQueryUi1$m_DownloadFileTypeDropDownList$m_DownloadFileType': '.xls',
            'ctl00$Main$q2_btn_Query': '查詢',
        }

    @property
    def kw(self) -> str:
        return self.__KEYWORD

    @property
    def days(self) -> list:
        return self.__DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]

    def set_years(self, year):
        self.form_data['ctl00$Main$CompareQueryUi1$q1_ddl_years'] = str(year)

    def set_months(self, month):
        self.form_data['ctl00$Main$CompareQueryUi1$q1_ddl_months'] = str(month)


class AgrstatBookCreator(BaseCreator):
    __KEYWORD = '{}年'
    __NUMBER_OF_PIG_KEYWORD = '{}年{}月底'
    __SELECT_DICT = {
        'a': '#ctl00_cphMain_uctlBook_repChapter_ctl07_dtlFile_ctl01_lnkFile',
        'a2': '#ctl00_cphMain_uctlBook_repChapter_ctl09_dtlFile_ctl01_lnkFile',
        'a3': '#ctl00_cphMain_uctlBook_repChapter_ctl56_dtlFile_ctl01_lnkFile',
        'a4': '#ctl00_cphMain_uctlBook_repChapter_ctl00_lnkChapter',
        'a5': '#ctl00_cphMain_uctlBook_repChapter_ctl02_dtlFile_ctl02_lnkFile',
        'a6': '#ctl00_cphMain_uctlBook_repChapter_ctl26_dtlFile_ctl00_lnkFile',
        'a7': '#ctl00_cphMain_uctlBook_repChapter_ctl10_dtlFile_ctl01_lnkFile',
        'a8': '#ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl01_lnkFile',
    }

    def __init__(self, kw):
        if kw == '糧食供需統計':
            self.__spec_day = '10011700'
            self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a']
            self.__form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl03$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.PROVISION_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.PROVISION_EVENTVALIDATION
            }
        elif kw == '畜產品生產成本':
            self.__spec_day = '07171700'
            self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a4']
            self.__form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl06$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.LIVESTOCK_PRODUCT_COST_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.LIVESTOCK_PRODUCT_COST_EVENTVALIDATION
            }
        elif kw == '毛豬飼養頭數':
            self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a5']
            self.__form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl08$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.NUMBER_OF_PIG_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.NUMBER_OF_PIG_EVENTVALIDATION
            }

        elif kw in ['畜禽產品生產量值', '畜禽飼養及屠宰頭（隻）數', '農作物種植面積、產量', '畜牧用地面積', '農業及農食鏈統計']:
            if kw == '畜禽產品生產量值':
                self.__spec_day = '04301700'
                self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a8']
            elif kw == '畜禽飼養及屠宰頭（隻）數':
                self.__spec_day = '04301700'
                self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a7']
            elif kw == '農作物種植面積、產量':
                self.__spec_day = '05311700'
                self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a2']
            elif kw == '農業及農食鏈統計':
                self.__spec_day = '12101600'
                self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a6']
            else:
                self.__spec_day = '04301700'
                self.__a_tag = AgrstatBookCreator.__SELECT_DICT['a3']

            self.__form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl09$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.CROP_AREA_YIELD_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.CROP_AREA_YIELD_EVENTVALIDATION
            }

        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=3bv2ewyqvboe2y45g52hri55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx',
        }
        super().__init__(headers)

    @property
    def kw(self):
        return self.__KEYWORD

    @property
    def date(self):
        return self.__NUMBER_OF_PIG_KEYWORD

    @property
    def tag(self):
        return self.__a_tag

    @property
    def day(self):
        return self.__spec_day


class ApisAfaCreator(BaseCreator):
    __KEYWORD = '{}年{}月'
    __DAY = ['', 15, 21, 15, 16, 15, 15, 16, 15, 17, 15, '05', '05']
    __SELECT_DICT = {
        'tr': '#WR1_1_WG1 > tbody > tr',
        'month_start': 'WR1_1_Q_PRSR_Month1_C1',
        'month_end': 'WR1_1_Q_PRSR_Month2_C1',
        'check_box_grape': 'WR1_1_PRMG_02_54',
        'search_button': 'CSS_ABS_NormalLink',
    }

    @property
    def kw(self) -> str:
        return self.__KEYWORD

    @property
    def days(self) -> list:
        return self.__DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class PirceNaifCreator(BaseCreator):
    __DAY = ['', 15, 21, 15, 16, 15, 15, 16, 15, 17, 15, 15, 17]
    __SELECT_DICT = {
        'option': '#ContentPlaceHolder_content_DropDownList_month > option'
    }

    @property
    def days(self) -> list:
        return self.__DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class BliCreator(BaseCreator):
    __KEYWORD = '{}年{}月'
    __ELDER_DAY = ['', 22, 21, 20, 20, 21, 20, 20, 20, 20, 15, 15, 17]
    __URL = 'https://www.bli.gov.tw/reportM.aspx?m=107{}&f=a7010'
    __SELECT_DICT = {
        'a': 'body > p:nth-of-type(2) > a:nth-of-type(1)',
    }

    @property
    def kw(self):
        return self.__KEYWORD

    @property
    def url(self):
        return self.__URL

    @property
    def days(self) -> list:
        return self.__ELDER_DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class PxwebCreator(BaseCreator):
    __SPEC_DAY = '01021700'
    __KEYWORD = '{}年'
    __URL = 'http://210.69.71.166/Pxweb2007/Dialog/varval.asp?ma=AG0005B2A&ti=%B9A%C2%B3%B8p%B2%CE%ADp%B8%EA%AE%C6%AEw' \
          '(%A6~)&path=../PXfile\CountyStatistics\%BBO%C6W%C2%B3%AD%B9%B2%CE%ADp%ADn%C4%FD\AG%C2%B3%ACF%C0%F4%B9%D2' \
          '\%A4%A4%A4%E5&lang=9&Flag=Q,_newtarget='

    __SELECT_DICT = {
        'all': '//td[@class="tdtop"][2]/a[contains(text(), "全選")]'
    }

    def __init__(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'ASPSESSIONIDASDTCRAB = HFDNLILCEOHHAINOMMLLJKML',
            'Host': '210.69.71.166',
            'Origin': 'http://210.69.71.166',
            'Referer': 'http://210.69.71.166/Pxweb2007/Dialog/varval.asp?ma=AG0005B2A&ti=%B9A%C2%B3%B8p%B2%CE%ADp%B8%EA%'
                       'AE%C6%AEw(%A6~)&path=../PXfile\CountyStatistics\%BBO%C6W%C2%B3%AD%B9%B2%CE%ADp%ADn%C4%FD\AG%C2%B3'
                       '%ACF%C0%F4%B9%D2\%A4%A4%A4%E5&lang=9&Flag=Q,_newtarget=',
        }
        super().__init__(headers)
        self.__form_data = {
            'strList': '',
            'var1': '(unable to decode value)',
            'var2': '(unable to decode value)',
            'var3': '(unable to decode value)',
            'Valdavarden1': '1',
            'Valdavarden2': '32',
            'Valdavarden3': '1',
            'varparm': 'ma=AG0005B2A&ti=%B9A%C2%B3%B8p%B2%CE%ADp%B8%EA%AE%C6%AEw%28%A6%7E%29&path=%2E%2E%2FPXfile%'
                       '5CCountyStatistics%5C%BBO%C6W%C2%B3%AD%B9%B2%CE%ADp%ADn%C4%FD%5CAG%C2%B3%ACF%C0%F4%B9%D2'
                       '%5C%A4%A4%A4%E5&xu=&yp=&lang=9',
        }

    @property
    def kw(self):
        return self.__KEYWORD

    @property
    def url(self):
        return self.__URL

    @property
    def day(self) -> str:
        return self.__SPEC_DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class AgrCostCreator(BaseCreator):
    __DAY = '07161700'
    __KEYWORD = '{}年期'
    __ITEM = ['雜糧', '蔬菜', '特用作物及花卉', '果品']
    __SELECT_DICT = {
        'year': 'WR1_1$Q_COD_Year_S$C1',
        'item': 'WR1_1_Q_COD_Group_C1',
        'submit': 'CSS_ABS_NormalLink',
        'a': 'a.CSS_AGBS_GridLink',
        'td3': '#WR1_1_WG1 > tbody > tr > td:nth-of-type(3)',
        'td9': '//*[@id="WR1_1_WG1_B_A"]/tbody/tr/td/table/tbody/tr/td[9]',
    }

    @property
    def day(self) -> str:
        return self.__DAY

    @property
    def kw(self):
        return self.__KEYWORD

    @property
    def item(self) -> list:
        return self.__ITEM

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]


class FishYearCreator(BaseCreator):
    __SPEC_DAY = '08301700'
    __KEYWORDS_LENTH = 7
    __KEYWORD = '民國{}年'
    __SELECT_DICT = {
        'a': 'table.list > tr:nth-of-type(2) > td:nth-of-type(2) > a'
    }

    def __init__(self):
        headers = {
            'Cookie': '_ga=GA1.3.1706750957.1534403345; __utmz=42899762.1534403345.1.1.utmcsr=(direct)|utmccn=(direct)|'
                      'utmcmd=(none); ASP.NET_SessionId=frxnma55dswkkpaoukxmxq55; _gid=GA1.3.1822684352.1544522012; '
                      '__utmc=42899762; citrix_ns_id=Xk1Z85fdC/0dbElJvGKrtuyZLaM0001; '
                      '__utma=42899762.1706750957.1534403345.1544580541.1544667115.9; '
                      '__atuvc=3%7C50; __atuvs=5c11bfebadae1349000; __utmb=42899762.2.10.1544667115',
            'Host': 'www.fa.gov.tw',
        }
        super().__init__(headers)

    @property
    def kw(self):
        return self.__KEYWORD

    @property
    def day(self):
        return self.__SPEC_DAY

    @classmethod
    def tag(cls, key) -> str:
        return cls.__SELECT_DICT[key]

    @staticmethod
    def len():
        return FishYearCreator.__KEYWORDS_LENTH