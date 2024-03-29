# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode
from PySide2.QtCore import QDate, QUrl, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QDialog, QTableView, QApplication, QAction
from PySide2.QtGui import QCursor, QColor, QBrush, QDesktopServices
from utils.util import average_line

from .charts import Ui_Dialog
from .myfund_qsql_table_model import MyFundQSqlTableModel


class MyFundTableView(QTableView):
    def __init__(self, parent=None):
        super(MyFundTableView, self).__init__(parent)
        self._parent = parent
        self.doubleClicked.connect(self.show_dialog)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        option = QAction(self)
        option.setText('删除')
        option.triggered.connect(self.del_)

        self.addAction(option)

        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.change_sort)

    def change_sort(self, column_index, order):
        self.model().setSort(column_index, order)
        self.model().select()

    def del_(self):
        selected_row = self.selectedIndexes()[0].row()
        self.model().removeRow(selected_row)
        self.model().select()

    def setDb(self, db):
        model = MyFundQSqlTableModel(self, db)
        self.setModel(model)
        self.setColumnHidden(0, True)
        self.setColumnWidth(2, 200)
        self.setColumnWidth(11, 200)
        self.setColumnWidth(12, 200)

    def show_dialog(self, index):
        if index.column() == 1:
            fund_code = self.model().record(index.row()).value('code')
            QDesktopServices.openUrl(QUrl('http://fund.eastmoney.com/{}.html'.format(fund_code)))
        if index.column() == 2:
            fund_code = self.model().record(index.row()).value('code')
            fund_name = self.model().record(index.row()).value('name')
            dialog = ChartsDialog(
                parent=self, fund_code=fund_code, fund_name=fund_name)
            dialog.show()


class ChartsDialog(Ui_Dialog, QDialog):
    def __init__(self, parent=None, fund_code=None, fund_name=None):
        super(ChartsDialog, self).__init__(parent)
        self.setupUi(self)

        self.desktop = QApplication.desktop()
        self.resize(self.desktop.screenGeometry().width(),
                    self.desktop.screenGeometry().height())

        self.fund_code = fund_code
        self.fund_name = fund_name
        self.label_fund_name.setText(
            '{}({})'.format(self.fund_name, self.fund_code))
        self.start_time.setDate(QDate.fromString((datetime.now() + timedelta(days=-60)
                                                  ).strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_time.setDate(QDate.currentDate())
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setCalendarPopup(True)
        self.end_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.change_start_time)
        self.end_time.dateChanged.connect(self.change_end_time)
        self.web_engine_view = QWebEngineView()

        charts = self.get_charts()
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))
        self.verticalLayout.addWidget(self.web_engine_view)

    def change_start_time(self, date):
        charts = self.get_charts(start_time=date.toString(
            'yyyy-MM-dd'), end_time=self.end_time.date().toString('yyyy-MM-dd'))
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))

    def change_end_time(self, date):
        charts = self.get_charts(start_time=self.start_time.date().toString(
            'yyyy-MM-dd'), end_time=date.toString('yyyy-MM-dd'))
        self.web_engine_view.load(QUrl.fromLocalFile(charts.render()))

    def get_charts(self, start_time=None, end_time=None):
        if start_time is None and end_time is None:
            start_time = (datetime.now() + timedelta(days=-60)
                          ).strftime('%Y-%m-%d')

        js_code = '''
        function(params){
            var str = params.data.name.date +'<br/>';
            str += '累计净值: '+ params.data.value+'<br/>';
            str += '5日均线偏离: '+ params.data.name.d5+'%<br/>';
            str += '10日均线偏离: '+ params.data.name.d10+'%<br/>';
            str += '15日均线偏离: '+ params.data.name.d15+'%<br/>';
            str += '30日均线偏离: '+ params.data.name.d30+'%<br/>';
            str += '60日均线偏离: '+ params.data.name.d60+'%<br/>';
            return str;
        }
        '''

        df = average_line(self.fund_code, start_time, end_time)

        line = Line(init_opts=opts.InitOpts(
            bg_color='#fff', width='{}px'.format(self.width() - 100), height='{}px'.format(self.height() - 100)))
        line.add_xaxis(df.index.tolist())

        data = df.T.to_dict()
        data = [opts.LineItem({**v, **{'date': k}}, v.get('unit_value'))
                for k, v in data.items()]

        line.add_yaxis('单位净值', data,
                       tooltip_opts=opts.TooltipOpts(formatter=JsCode(js_code)))

        # line.add_yaxis('m5', df['m5'].tolist(),
        #                is_symbol_show=True, is_smooth=True)
        line.add_yaxis('m10', df['m10'].tolist(),
                       is_symbol_show=True, is_smooth=True)
        # line.add_yaxis('m15', df['m15'].tolist(),
        #                is_symbol_show=True, is_smooth=True)
        line.add_yaxis('m20', df['m20'].tolist(),
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
            yaxis_opts=opts.AxisOpts(min_='dataMin'),
        )
        line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        return line
