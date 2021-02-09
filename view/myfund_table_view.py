# -*- coding:utf-8 -*-
from PySide2.QtWidgets import QTableView
from .myfund_qsql_table_model import MyFundQSqlTableModel


class MyFundTableView(QTableView):
    def __init__(self, parent=None):
        super(MyFundTableView, self).__init__(parent)
        self._parent = parent

    def setDb(self, db):
        model = MyFundQSqlTableModel(self, db)
        self.setModel(model)
        self.setColumnHidden(0, True)
