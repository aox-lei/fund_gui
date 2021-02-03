# -*- coding:utf-8 -*-
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import akshare as ak
import qdarkstyle
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QCompleter, QHeaderView,
                             QMainWindow, QTableWidget, QTableWidgetItem)
from tinydb import Query, TinyDB

from main_window import Ui_MainWindow

ROOT_PATH = Path.cwd()
DATA_PATH = ROOT_PATH.joinpath('data.txt')
db = TinyDB(ROOT_PATH.joinpath('db.json'))
Query = Query()


class MainWindow(QMainWindow, Ui_MainWindow):
    search_completer = None
    # 表格列和索引对应关系, 顺序不能改
    table_fund_column = ['code', 'name', 'type', 'yesterday_unit_value',
                         'assess_unit_value', 'assess_enhance_rate', 'hold_cost', 'hold_money', 'assess_profit']

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.resetUi()

        self.line_search.textChanged.connect(self.init_search)
        self.init_data()
        self.flush_assess_timer()

        self.render_table()
        self.table_fund.cellChanged.connect(self.update_table)

    def update_table(self, row, column):
        text = self.table_fund.item(row, column).text()
        fund_code = self.table_fund.item(row, 0).text()

        key = self.table_fund_column[column]
        db.update({key: text}, Query.code == fund_code)

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

    def click_search_completer(self):
        text = self.line_search.text()
        text = text.split('|')
        data = {
            'code': text[0],
            'name': text[1],
            'type': text[2]
        }
        self.replace_fund_data(data)

    def render_table(self):
        data = db.all()
        if not data:
            return True
        row_count = len(data)

        self.table_fund.setRowCount(row_count)
        for index, info in enumerate(data):
            for k, v in info.items():
                if k in self.table_fund_column:
                    _index = self.table_fund_column.index(k)
                    item = QTableWidgetItem(v)
                    if k not in ['hold_cost', 'hold_money']:
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table_fund.setItem(index, _index, item)

    def replace_fund_data(self, data):
        if db.search(Query.code == data.get('code')):
            db.update(data, Query.code == data.get('code'))
        else:
            if 'hold_cost' not in data:
                data['hold_cost'] = 0
            if 'hold_money' not in data:
                data['hold_money'] = 0
            db.insert(data)
        self.render_table()

    def init_data(self):
        self.thread = InitDataThread()
        self.thread.finished.connect(self.init_search)
        self.thread.start()

    def flush_assess_timer(self):
        self.timer = QTimer(self)
        self.timer.start(3000)
        self.timer.timeout.connect(self.flush_assess)

    def flush_assess(self):
        self.flush_assess_thread = FlushAssessThread()
        self.flush_assess_thread.line_data.connect(self.replace_fund_data)
        self.flush_assess_thread.start()

    def resetUi(self):
        pass


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
    line_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(FlushAssessThread, self).__init__(parent)

    def run(self):
        data = db.all()
        if not data:
            return True
        fund_codes = [info.get('code') for info in data]
        df = ak.fund_em_value_estimation()
        df = df[df['基金代码'].isin(fund_codes)]
        now = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        columns = {
            '基金代码': 'code',
            now + '-估算值': 'assess_unit_value',
            now + '-估算增长率': 'assess_enhance_rate',
            yesterday + '-单位净值': 'yesterday_unit_value'
        }
        df.rename(columns=columns, inplace=True)
        df = df[['code', 'assess_unit_value',
                 'assess_enhance_rate', 'yesterday_unit_value']]
        for index, row in df.iterrows():
            row_data = row.to_dict()
            fund_info = db.get(Query.code == row_data.get('code'))
            hold_cost = fund_info.get('hold_cost', 0)
            hold_money = fund_info.get('hold_money', 0)
            if hold_cost == '':
                hold_cost = 0
            if hold_money == '':
                hold_money = 0

            hold_cost = float(hold_cost)
            hold_money = float(hold_money)
            if hold_cost and hold_money:
                share = float(format(hold_money / hold_cost, '0.2f'))
                profit = float(format(
                    share * (float(row_data['yesterday_unit_value']) - float(row_data['assess_unit_value'])), '0.2f'))
                row_data['assess_profit'] = profit

            self.line_data.emit(row_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
