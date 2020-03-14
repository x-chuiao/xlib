from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from util import wrap_exception


class WebEngineView(QWebEngineView):
	def __init__(self, *args, **kwargs):
		super(WebEngineView, self).__init__(*args, **kwargs)
		# 绑定cookie被添加的信号槽
		# QWebEngineCookieStore * cookie = webView->page()->profile()->cookieStore();
		# cookie->deleteAllCookies();
		
		QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
		self.cookies = []

	@wrap_exception
	def onCookieAdd(self, cookie):  # 处理cookie添加的事件
		name = cookie.name().data().decode('utf-8')  # 先获取cookie的名字，再把编码处理一下
		value = cookie.value().data().decode('utf-8')  # 先获取cookie值，再把编码处理一下
		for cookie in self.cookies:
			if cookie['name'] == name:
				cookie['value'] = value
				break
		else:
			self.cookies.append({'name': name, 'value': value})

	# 获取cookie
	def get_cookie(self):
		return self.cookies
	
	def deleteAllCookies(self):
		self.page().profile().cookieStore().deleteAllCookies()
