# -*- coding:utf-8 -*-
import requests
import uuid
import json
from requests_html import HTML
import time
import decimal

decimal.getcontext().rounding = 'ROUND_HALF_UP'


def format_float(value, format='0.0000'):
    if not value:
        return 0
    return float(decimal.Decimal(value).quantize(decimal.Decimal(format)))


def get_uuid():
    return str(uuid.uuid1()).upper()


def get_fund_assess(fund_codes):
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
    print(data)
    if data.get('Success') == True:
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

        fund_data.append({
            'code': v.get('FCODE'),
            'assess_unit_value': assess_unit_value,
            'assess_enhance_rate': assess_enhance_rate,
            'yesterday_unit_value': v.get('NAV'),
        })
    return fund_data


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
