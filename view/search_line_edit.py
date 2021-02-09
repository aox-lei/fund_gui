# -*- coding:utf-8 -*-
import json
from pathlib import Path

from config import DATA_PATH
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QCompleter, QLineEdit


class SearchLineEdit(QLineEdit):
    search_completer = None

    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)
        self.textChanged.connect(self.init_search)

    def set_completer_callback(self, callback):
        self.completer_callback = callback

    def init_search(self, value=''):
        if value == '':
            value = self.text()

        if len(value) > 2 and self.search_completer is None:
            if not Path.exists(DATA_PATH):
                return True
            with open(DATA_PATH, 'r') as f:
                data = f.read()
            data = json.loads(data)
            self.search_completer = QCompleter(data)
            self.search_completer.setFilterMode(Qt.MatchContains)
            self.search_completer.setCompletionMode(QCompleter.PopupCompletion)

            self.search_completer.activated.connect(self.completer_callback)
            self.setCompleter(self.search_completer)
