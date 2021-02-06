# -*- coding:utf-8 -*-
import requests
import uuid


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
    if data.get('Success') == True:
        data = data.get('Datas')
    else:
        return False

    fund_data = []
    for k, v in enumerate(data):
        fund_data.append({
            'code': v.get('FCODE'),
            'assess_unit_value': v.get('GSZ'),
            'assess_enhance_rate': v.get('GSZZL'),
            'yesterday_unit_value': v.get('NAV')
        })
    return fund_data
