# -*- coding:utf-8 -*-
import sys
from pathlib import Path

import akshare as ak
import qdarkstyle
from PySide2.QtCore import Qt
from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit

from main_window import Ui_MainWindow

ROOT_PATH = Path.cwd()
DB_PATH = ROOT_PATH.joinpath('database.db').as_posix()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.connect_db()

        self.render_table()
        self.resetUi()

    def connect_db(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(DB_PATH)
        self.db.open()

    def render_table(self):
        self.table_model = MyFundQSqlTableModel(parent=self, db=self.db)
        self.table_fund.setModel(self.table_model)

    def resetUi(self):
        # 隐藏id字段
        self.table_fund.setColumnHidden(0, True)
        self.line_search = SearchLineEdit(self.centralwidget)


class SearchLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)


class MyFundQSqlTableModel(QSqlTableModel):
    """自定义基金表格

    Args:
        QSqlTableModel ([type]): [description]
    """
    headers = ['id', '基金代码', '基金名称', '基金类型', '前一日净值',
               '最新净值', '预估净值', '预估增长率', '持仓成本单价', '持仓份额', '持仓总金额', '预估收益']

    def __init__(self, parent=None, db=None):
        super(MyFundQSqlTableModel, self).__init__(parent, db)
        self.setTable('my_fund')
        for index, column in enumerate(self.headers):
            self.setHeaderData(index, Qt.Horizontal, column)
        self.setQuery(QSqlQuery(
            'SELECT id,code,name,type,prev_unit_value,unit_value,assess_unit_value,assess_growth_rate,hold_cost,hold_money,hold_share,assress_profit FROM my_fund'))
        self.select()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
