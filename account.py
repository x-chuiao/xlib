import json
import os
from collections import OrderedDict

import aiohttp
import requests
from enum import Enum


class LoginStatus(Enum):
	notlog = 0
	logging = 1
	logged = 2


class Account(object):
	"""
	根据cookies_file_hook设置cookies_file,可重新设置
	"""
	def __init__(self, name='', pwd='', cookies_dir=''):
		self.id = name
		self.nickname = None
		self.password = pwd
		self.status = LoginStatus.notlog
		self.cookies = []
		self.cookies_dir = cookies_dir
		self.cookies_file_name = self.cookies_file_hook(self.id)
	
	def set_cookies_file(self, name):
		self.cookies_file_name = name
	
	def set_cookies_dir(self, cookies_dir):
		self.cookies_dir = cookies_dir
	
	def get_cookies_path(self):
		return f'{self.cookies_dir}/{self.cookies_file_name}'
	
	def get_attr_list(self):
		return [self.id, self.password, self.nickname, self.status.value]
	
	def set_cookies(self, cookies):
		# 包含name和value键值3的字典的列表
		self.cookies = cookies
		self.save_cookies()
	
	def cookies_file_hook(self, file):
		return f'{file}'
	
	def reset(self):
		self.status = LoginStatus.notlog
		self.cookies = None
		if os.path.exists(self.cookies_file_name):
			os.remove(self.cookies_file_name)
	
	def makeAiohttpClientSession(self, **kargs):
		# 使用自带的cookie构造一个aiohttpSeesion对象
		kargs['cookie_jar'] = self.makeAiohttpCookiesJar(self.cookies)
		return aiohttp.ClientSession(**kargs)
	
	def makeAiohttpCookiesJar(self, cookies):
		# aiohttp.cookiejar 只接受cookie键值对
		cookies = [{cookie['name']: cookie['value']} for cookie in cookies]
		cookiejar = aiohttp.CookieJar()
		for item in cookies:
			cookiejar.update_cookies(item)
		return cookiejar
	
	def makeRequestsSession(self, **kargs):
		cookie_jar = self.makeRequestsCookieJar(self.cookies)
		session = requests.Session()
		session.cookies.update(cookie_jar)
		for key, value in kargs.items():
			if hasattr(session, key):
				setattr(session, key, value)
		return session
	
	def makeRequestsCookieJar(self, cookies):
		# 貌似只支持键值对
		cookie_jar = requests.cookies.RequestsCookieJar()
		for cookie in cookies:
			cookie_jar.set(cookie['name'], cookie['value'])
		return cookie_jar
	
	def loadCookiesList(self):
		if os.path.exists(self.cookies_file_name):
			self.cookies = json.load(open(self.get_cookies_path()))
	
	def save_cookies(self):
		# attr_list=['domain','expiry','httpOnly','name','path','secure','value']
		if not (self.cookies and self.cookies_dir):
			return
		json.dump(self.cookies, open(self.get_cookies_path(), 'w'))


class AccountManagement(object):
	def __init__(self, ac_path='', cookies_dir=''):
		self.accounts = OrderedDict()
		self.load(ac_path, cookies_dir)
		self._iter_ = self.accounts.__iter__()
	
	def set_cookies_dir(self, dir):
		for ac in self.accounts.values():
			ac.set_cookies_dir(dir)
	
	def load(self, ac_path='', cookies_dir=''):
		if os.path.isfile(ac_path):
			with open(ac_path) as f:
				for ip in f.read().split():
					id, pwd = ip.split('----')
					account = Account(id, pwd, cookies_dir)
					account.loadCookiesList()
					self.accounts[id] = account
	
	def save(self):
		for ac in self.accounts.values():
			ac.save_cookies()
	
	def __iter__(self):
		return self.accounts.__iter__()
	
	def next(self):
		v = None
		try:
			v = next(self._iter_)
		except Exception as e:
			self._iter_ = self.accounts.__iter__()
			print(e)
		return self.accounts.get(v)


if __name__ == '__main__':
	ac_mgt = AccountManagement(r'G:\Git\JdCartMonitor\jd\docs\accounts')
	v = ac_mgt.next()
	while v:
		print(v)
		v = ac_mgt.next()
