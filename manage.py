# -*- coding:utf-8 -*-
import sys
import qdarkstyle
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter
from PyQt5.QtCore import Qt
from main_window import Ui_MainWindow

items_list = ["C", "C++", "Java", "Python", "JavaScript",
              "C#", "Swift", "go", "Ruby", "Lua", "PHP"]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_search()

    def init_search(self):
        completer = QCompleter(items_list)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.line_search.setCompleter(completer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
