import asyncio
import os
from asyncio import Event

import sys
import pathlib
import re
import json
import inspect
import shutil
import traceback as tb

from .common import JsObject


def any(it, func=bool):
	"""
	对iter中的每个元素调用func,任意一个为真则返回True,否则为False

	:param it: 可迭代对象
	:param func: callable
	:return: True if any func(i) is true ,otherwise false
	"""
	for i in it:
		if func(i):
			return True
	return False


def headers2dict(headers: str):
	"""
	将一定规律的headers字符串转化为dict

	:param headers:字符串
	:return:标准json化的字符串
	"""
	headers = re.sub(r'^(?=\w)', "\"", headers, flags=re.M)
	headers = re.sub(r': ', "\":\"", headers)
	headers = re.sub(r'(?<=\S)$', "\",", headers, flags=re.M)
	return f'{{{headers[:-1]}}}'


def set_browser_cookies(browser, cookie_list):
	"""为selenium中的浏览器添加cookies"""
	browser.delete_all_cookies()
	for cookie in cookie_list:
		browser.add_cookie(cookie)


def auto_connect(cls: object, ui):
	"""
	适用于pyqt5的槽和对应控件的信号的自动连接.
	将该类中形如attr_name_event的函数,连接到attr_name字段的event属性上
	仅适用public方法

	:param cls:类对象
	:param ui:UI对象
	:return:
	"""
	for name in dir(cls):
		try:
			if '_' not in name or name.startswith('_'):
				continue
			method = getattr(cls, name)
			if not callable(method):
				continue
			attr, event = name.rsplit('_', 1)
			if not hasattr(ui, attr):
				continue
			attr = getattr(ui, attr)
			if not hasattr(attr, event):
				continue
			event = getattr(attr, event)
			if hasattr(event, 'connect'):
				event.connect(method)
			print(f'method {name} has connected')
		except Exception as e:
			print(f'auto_connect error:{e}')


def wrap_exception(func):
	"""
	捕获func抛出的异常,用于防止异常未被捕获而导致的崩溃
	todo:完善以适用于各种参数

	:param func: callable
	:return:
	"""
	
	def inner(*args, **kargs):
		try:
			# 仅传递func参数个数的参数,多余的参数将被忽略
			func(*args[:func.__code__.co_argcount], **kargs)
		except Exception as e:
			tb.print_exc()
	
	return inner


def mkfile(path=''):
	"""
	递归地创建文件
	"""
	os.makedirs(os.path.dirname(path))
	pathlib.Path(path).touch()


def is_file_name(name: str):
	"""
	是否是合法的文件名称,仅适用于windows
	:param name:
	:return:
	"""
	if len(name.encode()) > 256:
		return False
	if re.search(r'[\\/:*?"<>|]', name):
		return False
	return True


def update_dict(org: dict, up):
	"""
	未经过测试
	
	:param org:
	:param up:
	:return:
	"""
	if isinstance(up, list):
		for item in up:
			update_dict(org, item)
	elif isinstance(up, tuple):
		if up[0] in org:
			if isinstance(up[1], (tuple, list, dict)):
				update_dict(org[up[0]], up[1])
			else:
				org[up[0]] = up[1]
		else:
			if isinstance(org, dict):
				org[up[0]] = up[1]
			if isinstance(org, list):
				org.append(up)
	elif isinstance(up, dict):
		for item in up.items():
			if item[0] in org:
				if isinstance(item[1], (tuple, list, dict)):
					update_dict(org, item)
				else:
					org[item[0]] = item[1]
			else:
				org[item[0]] = item[1]


def wait_task_completed(task: asyncio.Task):
	if task.done() or task.cancelled():
		return
	signal = Event()
	task.add_done_callback(lambda x: signal.set())
	signal.wait()


def transforToManagerProxyObject(manager, data):
	"""将不转换dict中的key
	只支持基础数据，dict，list和tuple
	tuple将会转换成list
	result = data
	"""
	if isinstance(data, dict):
		result = manager.dict()
		for key in data:
			result[key] = transforToManagerProxyObject(manager, data[key])
	elif isinstance(data, list) or isinstance(data, tuple):
		result = manager.list()
		for item in data:
			result.append(transforToManagerProxyObject(manager, item))
	return result


def cancel_all_tasks(loop):
	for task in asyncio.Task.all_tasks(loop=loop):
		try:
			task.cancel()
		except:
			pass


def str2float(src: str):
	"""
	将小数点后两位的字符串转为对应float
	eg:2300->23.00
	"""
	src = list(src)
	src.insert(-2, '.')
	return float(''.join(src))


def decode(o):
	"""
	# 供json解码使用,将dict转为object
	:param o:
	:return:
	"""
	if isinstance(o, dict):
		r = JsObject()
		for key, value in o.items():
			setattr(r, key, value)
		return r
	return o


def format4json(file: str, encoding='utf8'):
	with open(file, encoding=encoding) as f:
		data = eval(f.read())
	json.dump(data, open(file, 'w', encoding=encoding), ensure_ascii=False, indent=1)


def acess_dict(d: dict, key_list: list):
	for key in key_list:
		d = d[key]
	return d


def parse_json(s):
	begin = s.find('{')
	end = s.rfind('}') + 1
	return json.loads(s[begin:end])


def reserve_dict_leaf(data: dict, func, *args, **kwargs):
	"""
	使用dfs遍历data,对每个叶子的元素调用func,func的签名应该像func(key,value,...)这样前两个参数用于接收键值
	:param data:f
	:param func:
	:return:
	"""
	que = list(data.items())
	while que:
		key, val = que.pop()
		if isinstance(val, dict):
			que.extend(val.items())
		else:
			func(key, val, *args, **kwargs)
			
def reserve_dict(data: dict, func, *args, **kwargs):
	"""
	按照dfs方式遍历字典,对每个元素调用func
	:param data: 
	:param func: 
	:param args: 
	:param kwargs: 
	:return: 
	"""
	que = list(data.items())
	while que:
		key, val = que.pop()
		if isinstance(val, dict):
			que.extend(val.items())
		func(key, val, *args, **kwargs)


if __name__ == '__main__':
	pass
