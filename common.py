import importlib
from configparser import ConfigParser


class ThreadStoppedException(BaseException):
	"""
	继承自BaseException类型,没有实现任何属性
	可设置为StopableThread线程抛出得异常
	"""
	pass


class SettingStorage(object):
	def __init__(self, setting_path: str, inject_module: str):
		self.setting_path = setting_path
		self.inject_module = inject_module
	
	def load(self):
		config = ConfigParser()
		config.read(self.setting_path)
		module = importlib.import_module(self.inject_module)
		default = config.defaults()
		for key in default:
			print(f'{key}:{default[key]}')
			if not hasattr(module, key):
				continue
			value: str = default[key]
			if value.isdigit():
				value = float(value)
			setattr(module, key, value)
	
	def dump(self):
		config = ConfigParser()
		module = importlib.import_module(self.inject_module)
		default = config.defaults()
		for v in [x for x in dir(module) if not x.startswith('_')]:
			default[v] = getattr(module, v)
		config.write(open(self.setting_path, 'w'))


class JsObject(object):
	"""
	object的直接子类,实现了动态增加属性,没有的属性返回空
	object无法动态增加属性
	"""
	def __getattr__(self, item):
		return None