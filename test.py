import util
from requests_html import HTML
import pandas as pd
cookie = 'cp_token=3154d5661c4b4f9e8aaea52d57002d21;st_inirUrl=;st_pvi=08446224274759;st_sp=2021-02-05%2020%3A01%3A15;ASP.NET_SessionId=3ucqsjk23parfraesbg0kpas;TradeLoginToken=d3930135ba6e4feda3c3b7629abfed65;st_si=64191009206197;st_sn=1;st_psi=20210206161039925-119085303933-6931175434;st_asi=delete;fund_login_qrid=a8b45e337c6f49f48ec6cf589b874be4;fund_trade_cn=jVT2EQcR5Q3pfQEnFrsH/IPUF6h+CajbXU2VHFYd/99GGum/H2xYnn/4PN2ZXT2xMNK2TzrhCRW9umw7+b5o3PytuH8KbcFlUYz3ihHwCis/qiM533Q=;fund_trade_name=j5WVgafTAEmGFlykZTCjB4TY7B/98osnbEMLPLIecsaOfr7JZxPE+X3b6osqeq2zYpIP8VU0;fund_trade_visitor=jGSRR3Qo0EmQAHlfMGCqmtFWJbb9BgC/T9QqPM8cmiwSXrf8xXBE+J3K4lBDVpOzPrkWJD4V;fund_trade_risk=j1gcTsxAxE1OjuamAdCf6oIRaI29+lDUrVgvPGmqB0FaKrMW9ksFWf3+It3aA5PzxISQfMgb;fund_trade_gps=7;VipLevel=2;UTOKEN=jVT2EQcR5Q3pfQEnFrsH/IPUF6h+CajbXU2VHFYd/99GGum/H2xYnn/4PN2ZXT2xMNK2TGrLJfKd7R22+NRj3/cJ2baLQTRYAlzGJK5HXOVTtJXUlbY=;LToken=b959bdd188e6480784fd33e40edc6a9a;fund_trade_trackid=pgyyc5JXuc5iwocNQmsTbQfdK2+i0wfGvOeppZBCtgsq+aZNUPG8F1vlE+ibtbjjg7iwLOdj3CtpdpNvwINDHQ==;'
response = util.get_hold_fund(cookie)
# data = response.json()
# import json
# data = json.loads(data.get('d'))
# data = '<table>{}</table>'.format(data.get('content'))
# html = HTML(html=data)
# fund_name = html.find('tr > td > p.f16 > a.lk')
# fund_name = [info.text for info in fund_name]
# fund_type = html.find('tr > td.tol.first > p.f12 > span.info-nopl')
# fund_type = [info.text for info in fund_type]
# new_unit_value = html.find('tr > td.tol.first > p.f12 > span:nth-child(2)')
# new_unit_value = [info.text for info in new_unit_value]
# for index, info in enumerate(new_unit_value):
#     _info = info.replace('最新净值：', '')
#     _info = _info.split('（')
#     new_unit_value[index] = _info[0]

# hold_money = html.find('tr > td.tor.f16.desc')
# hold_money = [info.text for info in hold_money]
# for index, info in enumerate(hold_money):
#     _info = info.split('\n')
#     hold_money[index] = _info[0].replace(',', '')

# data = []
# for index, info in enumerate(fund_name):
#     _info = info.split('（')
#     if fund_type[index] in ['高端理财']:
#         continue

#     data.append({
#         'name': _info[0],
#         'code': _info[1].strip('）'),
#         'fund_type': fund_type[index],
#         'yesterday_unit_value': float(new_unit_value[index]),
#         'hold_money': float(hold_money[index]),
#         'hold_cost': util.format_float(float(hold_money[index]) / float(new_unit_value[index]))
#     })
print(response)
