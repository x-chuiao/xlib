from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.Qt import pyqtSignal, pyqtSlot, QModelIndex

from .XAbstractTableModel import XAbstractTableModel
class TableModel(XAbstractTableModel):
	def __init__(self, data: list = None, hr_header: list = None, vl_header: list = None):
		"""
		使用给定的二维数据构造model,不考虑元素个数不相同的情况
		:param data:
		"""
		super().__init__()
		self._data = data or [[]]
		self._hr_header = hr_header or []
		self._vl_header = vl_header or []
	
	def rowCount(self, parent=None):
		return len(self._data)
	
	def columnCount(self, parent=None):
		return len(self._data[0])
	
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row = index.row()
		col = index.column()
		if role == Qt.DisplayRole:
			return self._format_column(col, self._data[row][col],row)
		return None
	
	def headerData(self, col, orientation, role):
		if role != Qt.DisplayRole:
			return
		if orientation == Qt.Vertical and self._vl_header:
			return str(self._vl_header[col])
		if orientation == Qt.Horizontal and self._hr_header:
			return str(self._hr_header[col])
		return None

	def set_data(self, data):
		self._data = data
		self.layoutChanged()
	
	def set_header(self, orientation, header):
		if orientation == Qt.Vertical:
			self._vl_header = header
		else:
			self._hr_header = header
		
