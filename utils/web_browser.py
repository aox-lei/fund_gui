from PySide2.QtCore import QUrl, Signal
from PySide2.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PySide2.QtWidgets import QWidget


class WebBrowser(QWebEngineView):
    cookies = {}
    close_browser = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(WebBrowser, self).__init__(*args, **kwargs)

        self.page().profile().cookieStore().cookieAdded.connect(
            self.onCookieAdd)
        self.loadFinished.connect(self.onLoadFinished)

    def onLoadFinished(self):
        def get_html(html):
            self.current_html = html
        self.current_url = self.page().url()

        self.page().toHtml(get_html)

    def closeEvent(self, event):
        self.close_browser.emit(self.cookies)

    def onCookieAdd(self, cookie):
        '''
        :param cookie: QNetworkCookie
        '''
        name = str(cookie.name().data(), encoding='utf-8')
        value = str(cookie.value().data(), encoding='utf-8')
        self.cookies[name] = value

    def get_cookies(self):
        return self.cookies

    def get_html(self):
        return self.current_html


def openWithWebBrowser(url):
    view = WebBrowser()
    view.load(QUrl(url))
    view.show()
    cookies = view.get_cookies()
    return cookies
