# -*- coding:utf-8 -*-
# %%
import akshare as ak
from datetime import datetime, timedelta
import pandas as pd
df = ak.fund_em_value_estimation()
df = df[df['基金代码'].isin(['161725'])]
now = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

columns = {
    '基金代码': 'code',
    now + '-估算值': 'today_unit_value',
    now + '-估算增长率': 'today_enhance_rate',
    yesterday + '-单位净值': 'yesterday_unit_value'
}
df.rename(columns=columns, inplace=True)
df[0]
# %%
