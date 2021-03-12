# -*- coding:utf-8 -*-
# %%
from requests_html import HTML, HTMLSession

session = HTMLSession()
response = session.get('http://www.baidu.com')
response.text