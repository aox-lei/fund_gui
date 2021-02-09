# -*- coding:utf-8 -*-
import sys
from pathlib import Path

import akshare as ak
import qdarkstyle
from PySide2.QtCore import Qt
from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import QApplication, QLineEdit, QMainWindow

from config import DB_PATH
from view.main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.line_search.set_completer_callback(self.search_completer)

        self.connect_db()
        self.table_fund.setDb(self.db)

    def connect_db(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(DB_PATH)
        self.db.open()

    def search_completer(self, text):
        text = text.split('|')
        data = {
            'code': text[0],
            'name': text[1],
            'type': text[2]
        }
        self.table_fund.model().add_row(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
