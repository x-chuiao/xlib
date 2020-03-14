

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.Qt import pyqtSignal, pyqtSlot, QModelIndex

class XAbstractTableModel(QAbstractTableModel):
	data_changed = pyqtSignal(QModelIndex,QModelIndex)
	layout_changed=pyqtSignal()
	def __init__(self):
		QAbstractTableModel.__init__(self)
		self.col_formatter = {}
		self.data_changed.connect(self._data_changed)
		self.layout_changed.connect(self._layout_changed)
		
	def _format_column(self, col, value, row):
		if col in self.col_formatter:
			func, args, kwargs = self.col_formatter[col]
			value = func(value, row, *args, **kwargs)
		return value
	
	def set_formatter(self, col, func, *args, **kwargs):
		"""func签名形式:func(value,row,*args,**kwargs),row为行索引"""
		self.col_formatter[col] = (func, args, kwargs)
	
	def get_column(self, col):
		return [row[col] for row in self._data if row]
	
	def append_row(self, data: list):
		self._data.append(data)
		self.layoutChanged()
	
	def _data_changed(self,top_left,bottom_rigth):
		super().dataChanged.emit(top_left,bottom_rigth, [])
		
	def dataChanged(self,top=None,left=None,bottom=None,right=None):
		if top is None and left is None:
			top_left=QModelIndex()
		else:
			top_left = self.createIndex(top,left)
		if bottom is None and right is None:
			bottom_right=QModelIndex()
		else:
			bottom_right = self.createIndex(bottom,right)
		self.data_changed.emit(top_left,bottom_right)
	
	def _layout_changed(self):
		super().layoutChanged.emit()
	
	def layoutChanged(self):
		self.layout_changed.emit()
	