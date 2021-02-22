# -*- coding:utf-8 -*-
import decimal
import json
import time
import uuid

import akshare as ak
import requests
from requests_html import HTML, HTMLSession
from datetime import datetime
decimal.getcontext().rounding = 'ROUND_HALF_UP'


def format_float(value, format_='0.0000'):
    """格式化数字为货币

    Args:
        value ([type]): [description]
        format (str, optional): [description]. Defaults to '0.0000'.

    Returns:
        [type]: [description]
    """
    if not value:
        return 0
    return float(decimal.Decimal(value).quantize(decimal.Decimal(format_)))


def to_datetime(date_str, format_='%Y-%m-%d'):
    return datetime.strptime(date_str, format_)


def to_str(date, format_='%Y-%m-%d'):
    return date.strftime(format_)


def get_uuid():
    return str(uuid.uuid1()).upper()


def get_fund_assess(fund_codes):
    """获取基金预估数据

    Args:
        fund_codes ([type]): [description]

    Returns:
        [type]: [description]
    """
    url = 'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFInfo'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'app-iphone-client-iPhone11',
        'clientInfo': 'ttjj-iPhone11,8-iOS-iOS14.4',
    }
    post_data = {
        'pageIndex': 1,
        'pageSize': 30,
        'Sort': '',
        'Fcodes': ','.join(fund_codes),
        'SortColumn': '',
        'isShowSe': False,
        'P': 'F',
        'deviceid': get_uuid(),
        'plat': 'Iphone',
        'product': 'EFund',
        'version': '6.3.8'
    }
    response = requests.post(url, headers=headers, data=post_data)
    data = response.json()

    if data.get('Success') == True:
        gz_time = data.get('Expansion').get('GZTIME')
        data = data.get('Datas')
    else:
        return False

    fund_data = []
    for k, v in enumerate(data):
        try:
            assess_unit_value = float(v.get('GSZ'))
        except Exception as e:
            assess_unit_value = 0
        try:
            assess_enhance_rate = float(v.get('GSZZL'))
        except Exception as e:
            assess_enhance_rate = 0

        _data = {
            'code': v.get('FCODE'),
            'assess_unit_value': float(assess_unit_value),
            'assess_growth_rate': float(assess_enhance_rate),
            'unit_value': float(v.get('NAV')),
        }
        if v.get('GZTIME') != '--':
            if v.get('PDATE') == to_str(to_datetime(v.get('GZTIME'), '%Y-%m-%d %H:%M')):
                # 如果最新净值已经更新, 则根据当前净值和增长率计算昨日净值
                _data['prev_unit_value'] = Formula.prev_unit_value(
                    _data.get('unit_value'), _data.get('assess_growth_rate'))
            else:
                _data['prev_unit_value'] = float(v.get('NAV'))

        fund_data.append(_data)
    return (fund_data, gz_time)


class Formula:
    @classmethod
    def prev_unit_value(cls, unit_value, enhance_rate):
        """根据当前净值和增长率计算昨日净值
        上一开放日净值 = 最新净值/(1+增长率/100)

        Args:
            unit_value ([type]): [description]
            enhance_rate ([type]): [description]

        Returns:
            [type]: [description]
        """
        return format_float(unit_value / (1 + enhance_rate / 100))

    @classmethod
    def nex_unit_value(cls, unit_value, enhance_rate):
        """根据当前净值推算下一日净值

        Args:
            unit_value ([type]): [description]
            enhance_rate ([type]): [description]

        Returns:
            [type]: [description]
        """
        return format_float(unit_value * (1 + enhance_rate / 100))

    @classmethod
    def hold_money(cls, unit_value, hold_share):
        """持仓总金额 = 最新净值*持有份额

        Args:
            unit_value ([type]): [description]
            hold_share ([type]): [description]

        Returns:
            [type]: [description]
        """
        return format_float(unit_value * hold_share)

    @classmethod
    def profit(cls, unit_value, prev_unit_value, hold_share):
        """收益 = (当前净值 - 上一日净值) / 持仓份额

        Args:
            unit_value ([type]): [description]
            prev_unit_value ([type]): [description]
            hold_share ([type]): [description]

        Returns:
            [type]: [description]
        """
        return format_float((unit_value - prev_unit_value) * hold_share)

    @classmethod
    def hold_share(cls, hold_money, unit_value):
        """持仓份额 = 持有总金额 / 单位净值

        Args:
            hold_money ([type]): [description]
            unit_value ([type]): [description]

        Returns:
            [type]: [description]
        """
        return format_float(hold_money / unit_value)


def get_hold_fund(cookie):
    """获取持仓信息

    Args:
        cookie ([type]): [description]
    """
    url = 'https://trade7.1234567.com.cn/MyAssets/do.aspx/GetHoldAssetsNew?{}'.format(
        int(time.time()))
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    }
    post_data = "{type:'0',sorttype:'5',isNeedTotal:true}"
    response = requests.post(url, headers=headers, data=post_data)
    data = response.json()
    data = json.loads(data.get('d'))
    data = '<table>{}</table>'.format(data.get('content'))

    html = HTML(html=data)
    fund_name = html.find('tr > td > p.f16 > a.lk')
    fund_name = [info.text for info in fund_name]
    fund_type = html.find('tr > td.tol.first > p.f12 > span.info-nopl')
    fund_type = [info.text for info in fund_type]
    new_unit_value = html.find('tr > td.tol.first > p.f12 > span:nth-child(2)')
    new_unit_value = [info.text for info in new_unit_value]
    for index, info in enumerate(new_unit_value):
        _info = info.replace('最新净值：', '')
        _info = _info.split('（')
        new_unit_value[index] = _info[0]

    hold_money = html.find('tr > td.tor.f16.desc')
    hold_money = [info.text for info in hold_money]
    for index, info in enumerate(hold_money):
        _info = info.split('\n')
        hold_money[index] = _info[0].replace(',', '')

    data = []
    for index, info in enumerate(fund_name):
        _info = info.split('（')
        if fund_type[index] in ['高端理财']:
            continue

        data.append({
            'name': _info[0],
            'code': _info[1].strip('）'),
            'type': fund_type[index],
            'yesterday_unit_value': float(new_unit_value[index]),
            'hold_money': float(hold_money[index]),
            'hold_cost': format_float(float(hold_money[index]) / float(new_unit_value[index]))
        })

    return data


class TtjjWeb(object):
    # 检测登录
    CHECK_LOGIN_URL = 'https://trade7.1234567.com.cn/do.aspx/CheckLogin'
    # 获取持仓列表
    HOLD_LIST_URL = 'https://trade7.1234567.com.cn/MyAssets/do.aspx/GetHoldAssetsNew?{}'.format(
        int(time.time()))
    HOLD_INFO_URL = 'https://trade.1234567.com.cn/myassets/single?iv=false&fc={fund_code}'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

    def __init__(self, cookie=None):
        self.cookie = cookie

    def set_cookie(self, cookie):
        self.cookie = cookie

    def check_login(self):
        """检测登录状态

        Returns:
            [type]: [description]
        """
        headers = {
            'User-Agent': self.USER_AGENT,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': self.cookie
        }
        response = requests.post(self.CHECK_LOGIN_URL, headers=headers)
        data = response.json()
        try:
            data = data.get('d')
            data = json.loads(data)
            name = data.get('Name')
            return name
        except Exception as e:
            return False

    def get_hold_list(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': self.cookie,
            'User-Agent': self.USER_AGENT,
        }
        post_data = "{type:'0',sorttype:'5',isNeedTotal:true}"
        response = requests.post(
            self.HOLD_LIST_URL, headers=headers, data=post_data)
        data = response.json()
        data = json.loads(data.get('d'))

        data = '<table>{}</table>'.format(data.get('content'))

        html = HTML(html=data)
        fund_name = html.find('tr > td > p.f16 > a.lk')
        fund_name = [info.text for info in fund_name]

        data = []
        for index, info in enumerate(fund_name):
            _info = info.split('（')
            fund_code = _info[1].strip('）')
            _data = self.get_hold_info(fund_code)
            if _data:
                data.append(_data)

        return data

    def get_hold_info(self, fund_code):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': self.cookie,
            'User-Agent': self.USER_AGENT,
        }
        session = HTMLSession()
        response = session.get(self.HOLD_INFO_URL.format(
            fund_code=fund_code), headers=headers)

        fund_type = response.html.find(
            'div.fr.section > div.head > div.clear > div.fl.w200.dashleft > ul:nth-child(1) > li:nth-child(1)', first=True)

        fund_type = fund_type.text.replace('产品类型：', '').replace('基金类型：', '')

        if fund_type in ['高端理财']:
            return False

        hold_money = response.html.find(
            'div.clear > div.balance > div:nth-child(3) > span:nth-child(1) > strong', first=True)

        hold_share = response.html.find(
            'div.clear > div.balance > div:nth-child(3) > span.ft.w220 > span', first=True)
        hold_cost = response.html.find('#tanbaodanjia > span', first=True)
        if hold_cost.text == '--':
            hold_cost = 0
        else:
            hold_cost = format_float(hold_cost.text.replace(',', ''))
        unit_value = response.html.find(
            'div.fr.section > div.head > div.h40.lh40 > span:nth-child(3) > strong', first=True)

        fund_name = response.html.find(
            'div.fr.section > div.head > div.h40.lh40 > h4 > a', first=True)
        fund_name = fund_name.text.split('(')[0]
        return {
            'hold_money': format_float(hold_money.text.replace(',', '')),
            'hold_share': format_float(hold_share.text.replace(',', '')),
            'hold_cost': hold_cost,
            'unit_value': format_float(unit_value.text.replace(',', '')),
            'type': fund_type,
            'name': fund_name,
            'code': fund_code
        }


def average_line(fund_code, start_time=None, end_time=None):
    assess_data = get_fund_assess([fund_code])

    gz_time = assess_data[1]
    assess_data = assess_data[0][0]

    df = ak.fund_em_open_fund_info(fund=fund_code, indicator="累计净值走势")
    now_date = datetime.strptime(
        gz_time, '%Y-%m-%d').date()
    if now_date not in df['净值日期'].unique():
        if assess_data.get('assess_growth_rate') != 0:
            df = df.append({
                '净值日期': now_date,
                '累计净值': Formula.nex_unit_value(df.iloc[-1]['累计净值'], assess_data.get('assess_growth_rate'))}, ignore_index=True)

    df = df[['净值日期', '累计净值']]
    df.rename(columns={
        '净值日期': 'date',
        '累计净值': 'unit_value'
    }, inplace=True)

    df['unit_value'] = df['unit_value'].astype('float')
    for v in [5, 10, 15, 20, 30, 60]:
        df['m{}'.format(v)] = df['unit_value'].rolling(v).mean()
        df['m{}'.format(v)] = df['m{}'.format(v)].round(4)
        df['d{}'.format(v)] = (df['unit_value'] -
                               df['m{}'.format(v)]) / df['m{}'.format(v)] * 100
        df['d{}'.format(v)] = df['d{}'.format(v)].round(2)

    if start_time and end_time:
        df = df[(df['date'] >= datetime.strptime(start_time, '%Y-%m-%d').date())
                & (df['date'] <= datetime.strptime(end_time, '%Y-%m-%d').date())]
    elif start_time:
        df = df[(df['date'] >= datetime.strptime(start_time, '%Y-%m-%d').date())]
    elif end_time:
        df = df[(df['date'] <= datetime.strptime(end_time, '%Y-%m-%d').date())]

    df.set_index(['date'], inplace=True)
    return df
