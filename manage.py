# -*- coding:utf-8 -*-
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import akshare as ak
import qdarkstyle
from PySide2.QtCore import Qt, QThread, Signal, QTimer
from PySide2.QtWidgets import (QApplication, QCompleter, QHeaderView,
                               QMainWindow, QAbstractItemView, QItemDelegate)
from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQuery

from main_window import Ui_MainWindow

ROOT_PATH = Path.cwd()
DATA_PATH = ROOT_PATH.joinpath('data.txt')
DB_PATH = ROOT_PATH.joinpath('database.db').as_posix()


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


class MainWindow(QMainWindow, Ui_MainWindow):
    search_completer = None
    # 表格列和索引对应关系, 顺序不能改

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.resetUi()

        self.line_search.textChanged.connect(self.init_search)
        self.init_db()

        self.flush_assess_timer()

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

            if hold_cost and hold_money:
                share = float(format(hold_money / hold_cost, '0.2f'))
                profit = float(format(
                    share * (float(data.get('assess_unit_value')) - float(data.get('yesterday_unit_value'))), '0.2f'))
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
        total_money = float(format(total_money, '0.2f'))
        profit_value = float(format(profit_value, '0.2f'))
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
        for i in [0, 1, 2, 3, 4, 5, 6, 9]:
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
        for index in range(0, model.rowCount() + 1):
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
        df = ak.fund_em_value_estimation()
        df = df[df['基金代码'].isin(fund_codes)]
        now = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        before_yesterday = (
            datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        columns = {
            '基金代码': 'code',
            now + '-估算值': 'assess_unit_value',
            now + '-估算增长率': 'assess_enhance_rate',
            yesterday + '-单位净值': 'yesterday_unit_value',
            yesterday + '-估算值': 'assess_unit_value',
            yesterday + '-估算增长率': 'assess_enhance_rate',
            before_yesterday + '-单位净值': 'yesterday_unit_value'
        }
        df.rename(columns=columns, inplace=True)

        df = df[['code', 'assess_unit_value',
                 'assess_enhance_rate', 'yesterday_unit_value']]
        for k, v in fund_list.items():
            _df = df[df['code'] == k]
            if len(_df) == 0:
                continue

            row = _df.iloc[-1]
            row_data = row.to_dict()
            self.line_data.emit(row_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
