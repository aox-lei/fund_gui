# -*- coding:utf-8 -*-
import decimal
import json
import time
import uuid

import akshare as ak
import requests
from requests_html import HTML
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


def check_login(cookie):
    url = 'https://trade7.1234567.com.cn/do.aspx/CheckLogin'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': cookie
    }
    response = requests.post(url, headers=headers)
    data = response.json()
    try:
        data = data.get('d')
        data = json.loads(data)
        name = data.get('Name')
        return name
    except Exception as e:
        return False


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
