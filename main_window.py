# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1238, 859)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_login_ttjj = QPushButton(self.centralwidget)
        self.btn_login_ttjj.setObjectName(u"btn_login_ttjj")
        self.btn_login_ttjj.setMinimumSize(QSize(120, 60))
        self.btn_login_ttjj.setMaximumSize(QSize(120, 60))

        self.horizontalLayout.addWidget(self.btn_login_ttjj)

        self.btn_sync = QPushButton(self.centralwidget)
        self.btn_sync.setObjectName(u"btn_sync")
        self.btn_sync.setMinimumSize(QSize(120, 60))
        self.btn_sync.setMaximumSize(QSize(120, 60))

        self.horizontalLayout.addWidget(self.btn_sync)

        self.line_search = QLineEdit(self.centralwidget)
        self.line_search.setObjectName(u"line_search")

        self.horizontalLayout.addWidget(self.line_search)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.table_fund = QTableView(self.centralwidget)
        self.table_fund.setObjectName(u"table_fund")
        self.table_fund.horizontalHeader().setHighlightSections(False)
        self.table_fund.verticalHeader().setCascadingSectionResizes(False)
        self.table_fund.verticalHeader().setHighlightSections(False)

        self.verticalLayout.addWidget(self.table_fund)

        self.label_total_money = QLabel(self.centralwidget)
        self.label_total_money.setObjectName(u"label_total_money")
        font = QFont()
        font.setPointSize(30)
        self.label_total_money.setFont(font)
        self.label_total_money.setStyleSheet(u"")
        self.label_total_money.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_total_money)

        self.label_assess = QLabel(self.centralwidget)
        self.label_assess.setObjectName(u"label_assess")
        self.label_assess.setFont(font)
        self.label_assess.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_assess)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_login_ttjj.setText(QCoreApplication.translate("MainWindow", u"\u767b\u5f55\u5929\u5929\u57fa\u91d1", None))
        self.btn_sync.setText(QCoreApplication.translate("MainWindow", u"\u540c\u6b65\u6301\u4ed3", None))
        self.line_search.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u57fa\u91d1\u4ee3\u7801, \u540d\u79f0", None))
        self.label_total_money.setText(QCoreApplication.translate("MainWindow", u"\u6301\u4ed3\u603b\u91d1\u989d: 200000\u5143", None))
        self.label_assess.setText(QCoreApplication.translate("MainWindow", u"2012-02-02 \u4f30\u7b97\u6536\u76ca\u4e3a10000\u5143, \u606d\u559c\u5403\u8089!", None))
    # retranslateUi

