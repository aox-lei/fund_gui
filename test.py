# -*- coding:utf-8 -*-
# %%
from utils import util
from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode
js_code = '''
        function(params){
            var str = params.data.name.date +'<br/>';
            str += '累计净值: '+ params.data.value+'<br/>';
            str += '5日均线偏离: '+ params.data.name.d5+'%<br/>';
            str += '10日均线偏离: '+ params.data.name.d10+'%<br/>';
            str += '30日均线偏离: '+ params.data.name.d30+'%<br/>';
            str += '60日均线偏离: '+ params.data.name.d60+'%<br/>';
            return str;
        }
        '''

df = util.average_line('000083', start_time='2021-02-01')
line = Line(init_opts=opts.InitOpts(bg_color='#fff'))
line.add_xaxis(df.index.tolist())


data = df.T.to_dict()

data = [opts.LineItem({**v, **{'date': k}}, v.get('unit_value'))
        for k, v in data.items()]

line.add_yaxis('单位净值', data,
               tooltip_opts=opts.TooltipOpts(formatter=JsCode(js_code)))

line.add_yaxis('m5', df['m5'].tolist(),
               is_symbol_show=True, is_smooth=True)
line.add_yaxis('m10', df['m10'].tolist(),
               is_symbol_show=True, is_smooth=True)
line.add_yaxis('m30', df['m30'].tolist(),
               is_symbol_show=False, is_smooth=True)
line.add_yaxis('m60', df['m60'].tolist(),
               is_symbol_show=False, is_smooth=True)

line.set_global_opts(
    xaxis_opts=opts.AxisOpts(
        axislabel_opts={"interval": "0",
                        "rotate": 180},
        is_show=False
    ),
    yaxis_opts=opts.AxisOpts(min_='dataMin')
)
line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
line.render()
# %%
