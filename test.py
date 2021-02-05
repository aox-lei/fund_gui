# -*- coding:utf-8 -*-
# %%
import akshare as ak
from datetime import datetime, timedelta
import pandas as pd
df = ak.fund_em_value_estimation()
df[df['基金代码'] == '000083']
# %%
