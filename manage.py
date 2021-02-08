# -*- coding:utf-8 -*-

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import akshare as ak
import qdarkstyle
from PySide2.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import (QAbstractItemView, QApplication, QCompleter,
                               QDoubleSpinBox, QHeaderView, QItemDelegate,
                               QMainWindow)

from main_window import Ui_MainWindow
from web_browser import WebBrowser, openWithWebBrowser
from util import get_fund_assess, check_login, format_float, get_hold_fund
ROOT_PATH = Path.cwd()
DATA_PATH = ROOT_PATH.joinpath('data.txt')
DB_PATH = ROOT_PATH.joinpath('database.db').as_posix()
COOKIE_PATH = ROOT_PATH.joinpath('cookie')


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() in [7, 8]:
            q = QDoubleSpinBox(option.widget)
            q.setDecimals(4)
            q.setRange(0, 10000000)
            q.setValue(float(index.data()))
            return q
        return None


class MainWindow(QMainWindow, Ui_MainWindow):
    search_completer = None
    # 表格列和索引对应关系, 顺序不能改

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.btn_login_ttjj.clicked.connect(self.open_web_browser)
        self.resetUi()

        self.line_search.textChanged.connect(self.init_search)
        self.btn_sync.clicked.connect(self.get_hold_fund)
        self.init_db()
        self.check_login()
        # self.flush_assess_timer()

    def open_web_browser(self):
        self.browser_view = WebBrowser()
        self.browser_view.load(QUrl(
            'https://login.1234567.com.cn/?direct_url=https%3a%2f%2ftrade.1234567.com.cn%2fMyAssets%2fDefault'))
        self.browser_view.show()

        self.browser_view.close_browser.connect(self.get_cookie)

    def get_cookie(self, cookies):
        if not cookies:
            return True
        cookie = ''
        for k, v in cookies.items():
            cookie += '{}={};'.format(k, v)
        with open(COOKIE_PATH, 'w') as f:
            f.write(cookie)

    def check_login(self):
        if not COOKIE_PATH.exists():
            return True
        with open(COOKIE_PATH, 'r') as f:
            cookies = f.read()
        result = check_login(cookies)
        if result:
            self.btn_login_ttjj.setText('登录成功')
            self.btn_login_ttjj.setEnabled(False)

    def get_hold_fund(self):
        if not COOKIE_PATH.exists():
            return True
        with open(COOKIE_PATH, 'r') as f:
            cookies = f.read()
        result = check_login(cookies)
        if not result:
            #TODO: 提示错误
            pass
        fund_data = get_hold_fund(cookies)

        if fund_data:
            for info in fund_data:
                self.model.flush_table(info)

    def init_db(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(DB_PATH)
        self.db.open()

        self.model = FundQSqlTableModel(
            parent=self, db=self.db, table_view=self.table_fund)

        self.table_fund.setModel(self.model)
        self.table_fund.setColumnHidden(0, True)
        self.update_label()

    def init_search(self, value=''):
        if value == '':
            value = self.line_search.text()

        if len(value) > 2 and self.search_completer is None:
            if not Path.exists(DATA_PATH):
                return True
            with open(DATA_PATH, 'r') as f:
                data = f.read()
            data = json.loads(data)
            self.search_completer = QCompleter(data)
            self.search_completer.setFilterMode(Qt.MatchContains)
            self.search_completer.setCompletionMode(QCompleter.PopupCompletion)

            self.search_completer.activated.connect(
                self.click_search_completer)
            self.line_search.setCompleter(self.search_completer)

    def click_search_completer(self, text):
        text = text.split('|')
        data = {
            'code': text[0],
            'name': text[1],
            'type': text[2]
        }
        self.model.flush_table(data)

    def init_data(self):
        self.thread = InitDataThread()
        self.thread.finished.connect(self.init_search)
        self.thread.start()

    def flush_assess_timer(self):
        self.timer = QTimer(self)
        self.timer.start(2000)
        self.timer.timeout.connect(self.flush_assess)

    def flush_assess(self):
        self.flush_assess_thread = FlushAssessThread(self)
        self.flush_assess_thread.line_data.connect(self.update_assess)
        self.flush_assess_thread.start()

    def update_assess(self, data):
        if self.table_fund.state() == QAbstractItemView.State.EditingState:
            return True
        match = self.model.match(self.model.index(
            0, 1), Qt.DisplayRole, data.get('code'))
        if match:
            row_index = match[0].row()
            row_record = self.model.record(row_index)
            hold_cost = row_record.value('hold_cost')
            hold_money = row_record.value('hold_money')

            for k, v in data.items():
                self.model.setData(self.model.index(
                    row_index, self.model.fieldIndex(k)), v)

            if hold_cost and hold_money and data.get('assess_unit_value') and data.get('yesterday_unit_value'):
                share = format_float(hold_money / hold_cost)
                profit = format_float(
                    share * (float(data.get('assess_unit_value')) - float(data.get('yesterday_unit_value'))))
                self.model.setData(self.model.index(
                    row_index, self.model.fieldIndex('assess_profit')), profit)
            else:
                self.model.setData(self.model.index(
                    row_index, self.model.fieldIndex('assess_profit')), 0)
        self.update_label()

    def update_label(self):
        q = QSqlQuery(
            'SELECT sum(hold_money) as total_money, sum(assess_profit) as profit FROM fund')
        q.first()
        total_money = q.value('total_money')
        if total_money is None:
            total_money = 0
        profit_value = q.value('profit')
        if profit_value is None:
            profit_value = 0
        total_money = format_float(total_money)
        profit_value = format_float(profit_value)
        self.label_total_money.setText(
            '持仓总金额:<b style="color:red">{}</b>元'.format(total_money))

        hour = datetime.now().hour
        if hour < 9:
            date = datetime.now().strftime('%Y-%m-%d')
        else:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        if profit_value > 0:
            self.label_assess.setText(
                '{}估算收益为<b style="color:red">{}</b>元, 恭喜老板吃肉!!'.format(date, profit_value))
        else:
            self.label_assess.setText(
                '{}估算收益为<b style="color:red">{}</b>元, 不要灰心, 继续补仓!'.format(date, profit_value))

    def resetUi(self):
        pass


class FundQSqlTableModel(QSqlTableModel):
    header_data = ['id', '基金代码', '基金名称', '基金类型', '昨日净值',
                   '估算净值', '估算增长率', '持仓成本单价', '持仓金额', '预估收益']

    def __init__(self, parent=None, db=None, table_view=None):
        super(FundQSqlTableModel, self).__init__(parent, db)
        self.table_view = table_view
        self.setTable('fund')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        for index, column in enumerate(self.header_data):
            self.setHeaderData(index, Qt.Horizontal, column)
        for i in range(0, len(self.header_data) + 1):
            self.table_view.setItemDelegateForColumn(
                i, EmptyDelegate(self))

        self.select()
        self.beforeInsert.connect(self.before_insert)

    def before_insert(self, record):
        default_rule = ['yesterday_unit_value', 'assess_unit_value',
                        'assess_enhance_rate', 'hold_cost', 'hold_money', 'assess_profit']
        for field in default_rule:
            if record.isNull(field):
                record.setValue(field, 0)

    def flush_table(self, data):
        math = self.match(self.index(
            0, 1), Qt.DisplayRole, data.get('code'))
        if not math:
            record = self.record()
            for k, v in data.items():
                record.setValue(k, v)
            result = self.insertRecord(self.rowCount(), record)
            if result:
                self.select()
            return False
        return True


class InitDataThread(QThread):
    def __init__(self):
        super(InitDataThread, self).__init__()

    def run(self):
        df = ak.fund_em_fund_name()
        df = df[['基金代码', '基金简称', '基金类型']]
        data = []
        for index, row in df.iterrows():
            data.append('{}|{}|{}'.format(
                row['基金代码'], row['基金简称'], row['基金类型']))
        with open(DATA_PATH, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False))


class FlushAssessThread(QThread):
    line_data = Signal(dict)

    def __init__(self, parent=None):
        self.parent = parent
        super(FlushAssessThread, self).__init__(parent)

    def run(self):
        fund_list = {}
        model = self.parent.model
        for index in range(0, model.rowCount()):
            _hold_cost = model.record(index).value('hold_cost')
            _hold_money = model.record(index).value('hold_money')
            if not _hold_cost:
                _hold_cost = 0
            if not _hold_money:
                _hold_money = 0
            fund_list[model.record(index).value('code')] = {
                'hold_cost': float(_hold_cost),
                'hold_money': float(_hold_money)
            }

        if not fund_list:
            return True
        fund_codes = list(fund_list.keys())
        if not fund_codes:
            return True
        for i in range(0, len(fund_codes), 30):
            fund_code = fund_codes[i:i + 30]
            assess_data = get_fund_assess(fund_code)
            if assess_data:
                for v in assess_data:
                    self.line_data.emit(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
