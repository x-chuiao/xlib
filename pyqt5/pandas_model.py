import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.Qt import pyqtSignal,QModelIndex
from .XAbstractTableModel import XAbstractTableModel 

class PandasModel(XAbstractTableModel):
	def __init__(self, data: pd.DataFrame):
		super().__init__()
		self._data = data

	def rowCount(self, parent=None):
		return self._data.shape[0]
	
	def columnCount(self, parnet=None):
		return self._data.shape[1]
	
	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():
			if role == Qt.DisplayRole:
				return str(self._data.iloc[index.row(), index.column()])
		return None
	
	def headerData(self, col, orientation, role):
		if role != Qt.DisplayRole:
			return
		if orientation == Qt.Vertical:
			return self._data.index[col]
		if orientation == Qt.Horizontal:
			return self._data.columns[col]
		return None


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication, QTableView
	
	df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
	                   'b': [100, 200, 300],
	                   'c': ['a', 'b', 'c']},index=('1','2','3'))
	app = QApplication(sys.argv)
	model = PandasModel(df)
	
	view = QTableView()
	view.setModel(model)
	view.resize(800, 600)
	view.show()
	from threading import Thread
	import time
	
	
	def mod():
		time.sleep(3)
		df.at['1', 'b'] = 400
		print(df.append(['xc',500,'d']))
		view.setModel(PandasModel(df))
		
	
	Thread(target=mod).start()
	sys.exit(app.exec_())
