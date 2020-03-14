from unittest import TestCase

from util import wrap_exception, auto_connect, mkfile


class Test(TestCase):
	def test_mkfile(self):
		mkfile('test/test/test')

	def _test_wrap_exception(self):
		class A:
			@wrap_exception
			def func(self, a):
				print(self)
				print(a)
				print('func')

		A().func(1, 3, 4, 5)

	def _test_auto_connect(self):
		class Object:
			pass

		class A:
			def __init__(self):
				self.btn = Object()
				self.btn.clicked = Object()
				self.btn.clicked.connect = lambda x: None
				auto_connect(self)

			def btn_clicked(self):
				pass

		a = A()

