import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

from account import AccountManagement, Account

from login import Ui_Dialog
from util import wrap_exception, auto_connect, is_file_name
from WebEngineView import WebEngineView


class LoginDialog(QDialog):
	def __init__(self, ac_mgt=None):
		super().__init__()
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		self.ui.browser = WebEngineView(self)
		# self.ui.browser.page().runJavaScript(js_input_func)
		self.ui.browser_layout.addWidget(self.ui.browser)
		self.ac_mgt = ac_mgt or AccountManagement('', '')
		self.ac = self.ac_mgt.next() or Account()
		
		self.update_curr_ac(self.ac)
		auto_connect(self, self.ui)
	
	def set_curr_ac(self,ac):
		self.ac=ac or Account()
		self.update_curr_ac(ac)
	
	def set_account_data(self, ac_mgt: AccountManagement):
		self.ac_mgt = ac_mgt or AccountManagement('', '')
		self.ac = self.ac_mgt.next() or Account()
		self.update_curr_ac(self.ac)
	
	def set_url(self, url):
		self.ui.url.setText(str(url))
	
	def set_cookies_path(self, path):
		self.ui.cookies_dir.setText(path)
	
	def set_ac_path(self, path):
		self.ui.id_path.setText(path)
	
	def update_curr_ac(self, ac):
		if isinstance(ac, Account):
			self.ui.id.setText(str(ac.id))
			self.ui.pwd.setText(str(ac.password))
			self.ui.cookies_file_name.setText(ac.cookies_file_name)
	
	@wrap_exception
	def next_btn_clicked(self):
		self.ac.set_cookies(self.ui.browser.get_cookie())
		self.ui.browser.deleteAllCookies()
		self.ui.browser.load(QUrl(self.ui.url.text()))
		ac=self.ac_mgt.next()
		if not ac:
			QMessageBox.warning(self,'警告','没有下一个了')
		self.set_curr_ac(ac)
	
	@wrap_exception
	def save_btn_clicked(self):
		self.ac_mgt.save()
	
	@wrap_exception
	def close_btn_clicked(self):
		self.close()
	
	@wrap_exception
	def load_btn_clicked(self):
		ac_path = self.ui.id_path.text()
		cookies_dir = self.ui.cookies_dir.text()
		if os.path.isfile(ac_path) and os.path.isdir(cookies_dir):
			self.set_account_data(AccountManagement(ac_path, cookies_dir))
		self.ui.browser.deleteAllCookies()
		self.ui.browser.load(QUrl(self.ui.url.text()))
	
	@wrap_exception
	def cookies_dir_editingFinished(self):
		self.ac_mgt.set_cookies_dir(self.ui.cookies_dir.text())
	
	@wrap_exception
	def cookies_file_name_editingFinished(self):
		name=self.ui.cookies_file_name.text()
		if is_file_name(name):
			QMessageBox.warning(self,'错误','请输入有效文件名')
			return
		self.ac.set_cookies_file(name)


if __name__ == '__main__':
	app = QApplication([])
	d = LoginDialog()
	d.ui.id_path.setText(r'G:\Git\JdCartMonitor\jd\docs\accounts')
	d.ui.cookies_dir.setText(r'D:\python36\Lib\site-packages\xlib\pyqt5\cookies')
	d.ui.url.setText(r'https://plogin.m.jd.com/login/login')
	d.show()
	app.exec()
