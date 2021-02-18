# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from pyecharts import options as opts
from pyecharts.charts import Line
from PySide2.QtCore import QUrl, QDate
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QDialog, QTableView
from utils.util import average_line

from .charts import Ui_Dialog
from .myfund_qsql_table_model import MyFundQSqlTableModel


class MyFundTableView(QTableView):
    def __init__(self, parent=None):
        super(MyFundTableView, self).__init__(parent)
        self._parent = parent
        self.doubleClicked.connect(self.show_dialog)

    def setDb(self, db):
        model = MyFundQSqlTableModel(self, db)
        self.setModel(model)
        self.setColumnHidden(0, True)

    def show_dialog(self, index):
        fund_code = self.model().record(index.row()).value('code')
        fund_name = self.model().record(index.row()).value('name')
        dialog = ChartsDialog(
            parent=self, fund_code=fund_code, fund_name=fund_name)
        dialog.show()


class ChartsDialog(Ui_Dialog, QDialog):
    def __init__(self, parent=None, fund_code=None, fund_name=None):
        super(ChartsDialog, self).__init__(parent)
        self.setupUi(self)
        self.fund_code = fund_code
        self.fund_name = fund_name
        self.label_fund_name.setText(
            '{}({})'.format(self.fund_name, self.fund_code))
        self.start_time.setDate(QDate.fromString((datetime.now() + timedelta(days=-30)
                                                  ).strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_time.setDate(QDate.currentDate())
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setCalendarPopup(True)
        self.end_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.change_start_time)
        self.web_engine_view = QWebEngineView()

        charts = self.get_charts()
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))
        self.verticalLayout.addWidget(self.web_engine_view)

    def change_start_time(self, date):
        charts = self.get_charts(start_time=date.toString('yyyy-MM-dd'))
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))

    def change_end_time(self, date):
        charts = self.get_charts(end_time=date.toString('yyyy-MM-dd'))
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))

    def get_charts(self, start_time=None, end_time=None):
        if start_time is None and end_time is None:
            start_time = (datetime.now() + timedelta(days=-30)
                          ).strftime('%Y-%m-%d')

        df = average_line(self.fund_code, start_time, end_time)
        line = Line(init_opts=opts.InitOpts(bg_color='#fff'))
        line.add_xaxis(df.index.tolist())
        line.add_yaxis('单位净值', df['unit_value'].tolist(), )
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
        return line
