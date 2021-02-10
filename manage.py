# -*- coding:utf-8 -*-
import json
import sys
from pathlib import Path

import akshare as ak
import qdarkstyle
from PySide2.QtCore import Qt, QThread, QTimer, Signal
from PySide2.QtSql import QSqlDatabase
from PySide2.QtWidgets import QApplication, QMainWindow

from config import DATA_PATH, DB_PATH
from view.main_window import Ui_MainWindow
from utils import util


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.line_search.set_completer_callback(self.search_completer)

        self.connect_db()
        self.table_fund.setDb(self.db)
        self.sync_fund_data()
        self.sync_fund_value_thread()

    def connect_db(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(DB_PATH)
        self.db.open()

    def sync_fund_data(self):
        self.sync_fund_thread = SyncFundDataThread()
        self.sync_fund_thread.start()

    def search_completer(self, text):
        text = text.split('|')
        data = {
            'code': text[0],
            'name': text[1],
            'type': text[2]
        }
        if not self.table_fund.model().find_code_index(data.get('code')):
            self.table_fund.model().add_row(data)

    def sync_fund_value_thread(self, fund_codes=None):
        if fund_codes is None:
            fund_codes = self.table_fund.model().get_fund_code_all()

        self.sync_fund_value_thread = SyncFundValueThread(self, fund_codes)
        self.sync_fund_value_thread.fund_data.connect(
            self.table_fund.model().update_row)
        self.sync_fund_value_thread.start()


class SyncFundDataThread(QThread):
    """每次启动都同步一次所有基金数据

    Args:
        QThread ([type]): [description]
    """

    def __init__(self):
        super(SyncFundDataThread, self).__init__()

    def run(self):
        df = ak.fund_em_fund_name()
        df = df[['基金代码', '基金简称', '基金类型']]
        data = []
        for index, row in df.iterrows():
            data.append('{}|{}|{}'.format(
                row['基金代码'], row['基金简称'], row['基金类型']))
        with open(DATA_PATH, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False))


class SyncFundValueThread(QThread):
    fund_data = Signal(dict)

    def __init__(self, parent=None, fund_codes=None):
        super(SyncFundValueThread, self).__init__(parent)
        self.fund_codes = fund_codes

    def run(self):
        if not self.fund_codes:
            return True

        for i in range(0, len(self.fund_codes), 30):
            fund_code = self.fund_codes[i:i + 30]
            assess_data = util.get_fund_assess(fund_code)
            if assess_data:
                for v in assess_data:
                    self.fund_data.emit(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
