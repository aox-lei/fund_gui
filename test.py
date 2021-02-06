# -*- coding:utf-8 -*-
# %%
import akshare as ak
from datetime import datetime, timedelta
import pandas as pd
df = ak.fund_em_value_estimation()
df[df['基金代码'] == '000083']
# %%
t = {'cp_token': 'daa2fdba75f747e192fb1741d90adb53', 'st_inirUrl': '', 'st_pvi': '08446224274759', 'st_sp': '2021-02-05%2020%3A01%3A15', 'ASP.NET_SessionId': 'b1nd3fipdr330pt1twiy3zwc', 'TradeLoginToken': '4f9e75e209c840cba516f1074a9ebb0e', 'st_si': '18642518925258', 'st_sn': '2', 'st_psi': '20210205214414987-119085303933-8280858184', 'st_asi': 'delete', 'fund_login_qrid': '9e259abb499d421cae2d390ff4781af2', 'fund_trade_cn': 'AIV5WUAzzeBQ9ZCSNpu0oA/hhbCBIWB7UTCGQc4DwNbkyKhmLiscP3zqadDLBBvGr0ccB7C2L3LBWTuqXNbgMZoEDQLkiq4X9mi4AiLz/DrNH9pKqjs=', 'fund_trade_name':
     'AurZUw0hDCsmZdZPtpIcsgQySOPb90x9SQfKaZBqT26vtC1y6p0MVjMHRR8ykoUiJqufjBq1', 'fund_trade_visitor': 'AIK4E9nrYC6p5cl1KVI5+xXcSgAbofHZSCCGaY2EPg9tqC/4D5dKzAM1fj6N1ldi9Q05AvmE', 'fund_trade_risk': 'AgTFebI5tCWtcBpJkLIe3XIaKDobWPDpVNgHa87Z72b4MCl/whZhkvMZbZfvzXjiKZYM1b/o', 'fund_trade_gps': '7', 'VipLevel': '2', 'UTOKEN': 'AIV5WUAzzeBQ9ZCSNpu0oA/hhbCBIWB7UTCGQc4DwNbkyKhmLiscP3zqadDLBBvGr0ccBVCCuYysnMYX+KLJMxtakZvaEgRelPiZe+z9c97xiZDXwto=', 'LToken': '11f33a5e262543fead110d8bf6af37d4', 'fund_trade_trackid': 'YA1Wv68Xp4vD6Pm2mVEtvufMjXWCPvaq+zJXBEUa4IifXjv9re1GeGhSOkSNuc5LiWwa8dZapvjvyFVmwGqh5A=='}
s = ''
for k, v in t.items():
    s += '{}={};'.format(k, v)
s
# %%
import decimal
decimal.getcontext().rounding = 'ROUND_HALF_UP'
a = decimal.Decimal(1.24).quantize(decimal.Decimal('0.0'))

a
# %%
import util
data = util.get_fund_assess(['161725'])
data

# %%
