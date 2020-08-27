from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QWidget, QGridLayout

import time
import traceback, sys
import queue
import collections
import pickle
import struct
import pyqtgraph as pg
import numpy as np
import random

import os

from pyftdi.spi import SpiController
from pyftdi.usbtools import UsbTools


plot_x_range = 4000
input_queue = queue.Queue(maxsize=1000)
plot_freq = 10
process_freq = 1000

coefs = []


global_flag = True
stop_flag = True
#global counter_global
#counter_global = 1





def set_file_name(string):
	settings.dic['file_name'] = string

def set_meas_freq(string):
	try:
		settings.dic['meas_freq'] = float(string)
		print(settings.dic['meas_freq'])
	except ValueError:
		pass

def set_time_meas(string):
	try:
		settings.dic['Time_meas'] = float(string)
		print(settings.dic['Time_meas'])
	except ValueError:
		pass

def set_spi_freq(string):
	try:
		settings.dic['spi_freq'] = float(string)
		print(settings.dic['spi_freq'])
	except ValueError:
		pass


class CustomViewBox(pg.ViewBox):
	def __init__(self, *args, **kwds):
		pg.ViewBox.__init__(self, *args, **kwds)
		# print('CustomViewBox init')
		#self.setMouseMode(self.RectMode)


	def wheelEvent(self, ev, axis=None):
		# 1. Pass on the wheelevent to the superclass, such
		#    that the standard zoomoperation can be executed.
		# pg.ViewBox.wheelEvent(self,ev,axis)
		# print('s')
		pass

		# 2. Reset the x-axis to its original limits
		#
		# [code not yet written]
		#


class Window(QWidget):
	def __init__(self):
		super().__init__()
		# self.setFocusPolicy(QtCore.Qt.StrongFocus)
		# self.setFocusPolicy(QtCore.Qt.NoFocus)


		self.initUI()
		self.simpleplot()
		# self.initTimer()

	def initUI(self):
		# self.guiplot = pg.PlotWidget()
		# CustomViewBox() перегрузка метода стандартного класса, чтобы подавить фокус от колесика
		# т.е. wheelEvent переопределяется пустым
		self.vb = CustomViewBox()
		self.guiplot = pg.PlotWidget(viewBox=self.vb, name='myPlotWidget')


		# pg.setConfigOptions(antialias=True)
		self.guiplot.setMouseEnabled(x=False, y=False)
		self.guiplot.hideAxis('bottom')
		# self.guiplot.setRange(xRange=(0,1000), yRange=(-2,2), disableAutoRange=True)

		
		layout = QGridLayout(self)
		layout.addWidget(self.guiplot, 0,0)

	def simpleplot(self):
		self.x = np.arange(plot_x_range)
		self.y = np.random.normal(size=(167))
		# self.curve = self.guiplot.plot(self.x, self.y, pen=(255,0,0))
		self.curve = self.guiplot.plot([0], [0], pen=pg.mkPen('r', width=1))
		# self.curve = self.guiplot.plot([0], [0], pen=(255,0,0))

	def plot_clear(self):
		print('Clear Gui')
		self.curve.clear()
		self.curve.setData([0], [0])
		# (data=[x,y], title="Three plot curves")

	# def initTimer(self):
	#   self.timer = QtCore.QTimer(self)
	#   self.timer.setInterval(16.666666666) # in milliseconds
	#   self.timer.start()
	#   self.timer.timeout.connect(self.update)
	#   # print('connecnted')

	@pyqtSlot()
	def update(self, y_data):
		#global counter_global
		# time.sleep(0.001)
		#self.curve.setData([0, 1000], [0, 1001], clear=True)
		#app.processEvents()
		self.curve.setData(self.x, y_data, clear=True)
		#counter_global += 1
		#print(counter_global)
		#app.processEvents()
		#pg.processEvents()
		# pass
		# del self.y
		# self.y = np.random.normal(size=(100))
		# # self.y = self.y[interval:]


		# # interval = 10
		# # self.x = self.x + interval
		# # self.y = self.y[interval:]
		# # self.y = np.append(self.y, np.random.normal(size=(interval)))

		# # print(self.x)
		# # print(self.y)
		# # time.sleep(0.5)
		# # print(self.x)
		# # print(self.y)


		# self.curve.setData(self.x, self.y)
		# # self.processEvents()



class settings(object):
	file_name = '__default_settings'

	@classmethod
	def defaults_init(cls):
		cls.dic = {'spi_freq': '5e6', 'meas_freq': '100', 'file_name': 'test_file.txt', 'spi_mode': '0', 'Time_meas': '2', 'timeout': '1'}
		cls.cs_1 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}
		cls.cs_2 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}
		cls.cs_3 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
		cls.cs_4 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
		cls.cs_5 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
		cls.cs_6 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}

	try:
		with open(file_name + '.pkl', 'rb') as f:
			dic = pickle.load(f)
			cs_1 = pickle.load(f)
			cs_2 = pickle.load(f)
			cs_3 = pickle.load(f)
			cs_4 = pickle.load(f)
			cs_5 = pickle.load(f)
			cs_6 = pickle.load(f)

			print(dic)
			print(cs_1)
			print(cs_2)
			print(cs_3)
			print(cs_4)
			print(cs_5)
			print(cs_6)

	except IOError:
		with open(file_name + '.pkl', 'wb') as f:
			# стандартные настройки
			dic = {'spi_freq': '5e6', 'meas_freq': '100', 'file_name': 'test_file.txt', 'spi_mode': '0', 'Time_meas': '2', 'timeout': '1'}
			cs_1 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}
			cs_2 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}
			cs_3 = {'State': True, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
			cs_4 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
			cs_5 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': False}
			cs_6 = {'State': False, 'coef_MMA': '1', 'coef_MMG': '5', 'MMA_MMG_flag': True}

			pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_1, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_2, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_3, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_4, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_5, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cs_6, f, pickle.HIGHEST_PROTOCOL)

	cs_list = [cs_1, cs_2, cs_3, cs_4, cs_5, cs_6]


	@classmethod
	def rewrite(cls):
		with open(cls.file_name + '.pkl', 'wb') as f:
			# стандартные настройки
			cls.defaults_init()

			ui.lineEdit_filename.setText(cls.dic['file_name'])
			ui.lineEdit_spiFreq.setText(cls.dic['spi_freq'])
			ui.lineEdit_measFreq.setText(cls.dic['meas_freq'])
			ui.lineEdit_Timemeas.setText(cls.dic['Time_meas'])

			ui.lineEdit_1_MMA_coeff.setText(cls.cs_1['coef_MMA'])
			ui.lineEdit_1_MMG_coeff.setText(cls.cs_1['coef_MMG'])
			ui.lineEdit_2_MMA_coeff.setText(cls.cs_2['coef_MMA'])
			ui.lineEdit_2_MMG_coeff.setText(cls.cs_2['coef_MMG'])
			ui.lineEdit_3_MMA_coeff.setText(cls.cs_3['coef_MMA'])
			ui.lineEdit_3_MMG_coeff.setText(cls.cs_3['coef_MMG'])
			ui.lineEdit_4_MMA_coeff.setText(cls.cs_4['coef_MMA'])
			ui.lineEdit_4_MMG_coeff.setText(cls.cs_4['coef_MMG'])
			ui.lineEdit_5_MMA_coeff.setText(cls.cs_5['coef_MMA'])
			ui.lineEdit_5_MMG_coeff.setText(cls.cs_5['coef_MMG'])
			ui.lineEdit_6_MMA_coeff.setText(cls.cs_6['coef_MMA'])
			ui.lineEdit_6_MMG_coeff.setText(cls.cs_6['coef_MMG'])

			pickle.dump(cls.dic, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_1, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_2, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_3, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_4, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_5, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_6, f, pickle.HIGHEST_PROTOCOL)

	@classmethod
	def close(cls):

		cls.dic['file_name'] = ui.lineEdit_filename.text()
		cls.dic['meas_freq'] = ui.lineEdit_measFreq.text()
		cls.dic['Time_meas'] = ui.lineEdit_Timemeas.text() # Поменять!!!
		cls.dic['spi_freq'] = ui.lineEdit_spiFreq.text()

		cls.cs_1['State'] = ui.pushButton_cs1.isChecked()
		cls.cs_1['MMA_MMG_flag'] = ui.pushButton_1_MMA.isChecked()
		cls.cs_1['coef_MMA'] = ui.lineEdit_1_MMA_coeff.text()
		cls.cs_1['coef_MMG'] = ui.lineEdit_1_MMG_coeff.text()

		cls.cs_2['State'] = ui.pushButton_cs2.isChecked()
		cls.cs_2['MMA_MMG_flag'] = ui.pushButton_2_MMA.isChecked()
		cls.cs_2['coef_MMA'] = ui.lineEdit_2_MMA_coeff.text()
		cls.cs_2['coef_MMG'] = ui.lineEdit_2_MMG_coeff.text()

		cls.cs_3['State'] = ui.pushButton_cs3.isChecked()
		cls.cs_3['MMA_MMG_flag'] = ui.pushButton_3_MMA.isChecked()
		cls.cs_3['coef_MMA'] = ui.lineEdit_3_MMA_coeff.text()
		cls.cs_3['coef_MMG'] = ui.lineEdit_3_MMG_coeff.text()

		cls.cs_4['State'] = ui.pushButton_cs4.isChecked()
		cls.cs_4['MMA_MMG_flag'] = ui.pushButton_4_MMA.isChecked()
		cls.cs_4['coef_MMA'] = ui.lineEdit_4_MMA_coeff.text()
		cls.cs_4['coef_MMG'] = ui.lineEdit_4_MMG_coeff.text()

		cls.cs_5['State'] = ui.pushButton_cs5.isChecked()
		cls.cs_5['MMA_MMG_flag'] = ui.pushButton_5_MMA.isChecked()
		cls.cs_5['coef_MMA'] = ui.lineEdit_5_MMA_coeff.text()
		cls.cs_5['coef_MMG'] = ui.lineEdit_5_MMG_coeff.text()

		cls.cs_6['State'] = ui.pushButton_cs6.isChecked()
		cls.cs_6['MMA_MMG_flag'] = ui.pushButton_6_MMA.isChecked()
		cls.cs_6['coef_MMA'] = ui.lineEdit_6_MMA_coeff.text()
		cls.cs_6['coef_MMG'] = ui.lineEdit_6_MMG_coeff.text()

		
		print(ui.pushButton_1_MMA.isChecked())

		
		with open(cls.file_name + '.pkl', 'wb') as f:
			pickle.dump(cls.dic, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_1, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_2, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_3, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_4, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_5, f, pickle.HIGHEST_PROTOCOL)
			pickle.dump(cls.cs_6, f, pickle.HIGHEST_PROTOCOL)


			# print(cls.dic)
			# print(cls.cs_1)
			# print(cls.cs_2)
			# print(cls.cs_3)
			# print(cls.cs_4)
			# print(cls.cs_5)
			# print(cls.cs_6)


class input_for_qrunnable_class(object):

	def __init__(self, parent=None):
		print('input_for_qrunnable_class __init__')
		self.timeout = 1


		pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]
		
		id_spi_to_run = []
		for i,k in enumerate(pushButton_cs):
			# pass
			if k:
				id_spi_to_run.append(i)


		self.file = open(settings.dic['file_name'], 'w')

		file_header = ''.join('angle ' + str(i + 1) + '\t\t' + 'temp ' + str(i + 1) + '\t\t' for i in id_spi_to_run)
		self.file.write(file_header)
		self.file.write('\n')


		spi_count = 2
		cs_count = 3
		self.spi = [SpiController(cs_count=cs_count, turbo=True) for i in range(0, spi_count)]      # Create channels for ech SPI
		self.slave = [None]*spi_count*cs_count
		self.plot_deque = []

		for i in range(6):
			self.plot_deque.append(collections.deque([0]*plot_x_range, maxlen=plot_x_range)) #1000
		
		for sp_i in range(0, spi_count):
			self.spi[sp_i].configure(url='ftdi://ftdi:4232h/' + str(sp_i + 1))
			for cs_i in range(0, cs_count):
				self.slave[sp_i*cs_count + cs_i] = (self.spi[sp_i].get_port(cs=cs_i, freq=float(settings.dic['spi_freq']), mode=int(settings.dic['spi_mode'])))
		print(self.slave)


	def execute_this_plot(self, process_callback, Worker):
		period = 1/60
		Num_iter = 0

		def g_tick():
			t = time.time()
			count = 0;
			while True:
				count += 1
				yield max(t + count*period - time.time(), 0)
		g = g_tick()

		start = time.clock()

		pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]
		
		plots_to_run = [ui.graphicsView1, ui.graphicsView2, ui.graphicsView3, ui.graphicsView4, ui.graphicsView5, ui.graphicsView6]

		id_plots_to_run = []
		for i,k in enumerate(pushButton_cs):
			# pass
			if k:
				id_plots_to_run.append(i)

		print(id_plots_to_run)

		temp_len = len(id_plots_to_run)


		#clear all plots
		for i in range(6):
			plots_to_run[i].plot_clear()


		while True:
			if not Worker.check_running():
				break

			time.sleep(next(g))

			for i in id_plots_to_run:
				plots_to_run[i].update(list(self.plot_deque[i]))
				process_callback.emit(i)
				# print(i)
				# time.sleep(0.5)

			# time.sleep(0.1)
			# app.processEvents()

		# print('update plot called, emulating plotting:', plot_deque)
		return "Done."

	def unpack_angle(self, read_buf):
		data = (((read_buf[1] & 0x3F) << 17) | (read_buf[2] << 9) | (read_buf[3] << 1) | ((read_buf[4] >> 7) & 0x01))
		if ((read_buf[1] >> 6) & 0x01) == 1:
			data = -1*( ( (~data) & 0x007FFFFF) + 1)
		data = data / 10000
		return data

	def execute_this_process(self, process_callback, Worker):
		while True:
			if not Worker.check_running():
				break

			if input_queue.empty():
				time.sleep(1/process_freq)
			
			if not input_queue.empty():
				
				i = input_queue.get(timeout=self.timeout)
				result = input_queue.get(timeout=self.timeout)
				multiplier = input_queue.get(timeout=self.timeout)

				# print(input_queue.queue)
				# self.plot_queue = 

				# time.sleep(0.1)

				# self.file.write('test')
				# for i in range(100):
					# time.sleep(0.01)
					# print('trying to interrupt, treat iter', i)
				if result != None:
					#time.sleep(0.5)
					#angle = np.frombuffer(result[1:-2], dtype='f4')[0]
					angle = self.unpack_angle(result)
					angle = angle*multiplier

					#time.sleep(0.1)
					#if not angle == None:
					#print(i, angle)
					#if not angle == None:
					self.plot_deque[i].append(angle)
					
					#else:
						#self.plot_deque[i].append(0)

					temp = result[-2:]
				# 	self.file.write(str(angle) + '\t' + str(struct.unpack("e", temp)[0]) + '\t')
				# 	try:
				# 		self.file.write(str(angle) + '\t' + str(struct.unpack("e", temp)[0]) + '\t')
				# 	except ValueError:
				# 		#print('ValueError in writing to file')
				# 		pass
				# else:
				# 	#self.file.write('\n')
				# 	# time.sleep(0.5)
				# 	# print('\n')
				# 	try:
				# 		self.file.write('\n')
				# 	except ValueError:
				# 		#print('ValueError in writing to file')
				# 		pass
		return "Done."

	def once_meas_blob(self, i):
		angle = random.randint(10, 1000)
		angle = bytearray(struct.pack("f", angle))
		return b'\x50' + angle + b'\x00\x00'
	
	def once_meas(self, i):             # DEBUG: Log for SPI
		read_buf = self.slave[i].exchange([0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], duplex=True)
		return read_buf

	def execute_this_input(self, process_callback, Worker):
		print('execute_this_input')

		pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]
		
		id_spi_to_run = []
		for i,k in enumerate(pushButton_cs):
			# pass
			if k:
				id_spi_to_run.append(i)

		meas_freq = float(settings.dic['meas_freq'])
		Time_meas = float(settings.dic['Time_meas'])


		period = 1/meas_freq
		function = self.once_meas
		Num_iter = 0


		def g_tick():
			t = time.time()
			count = 0;
			while True:
				count += 1
				yield max(t + count*period - time.time(), 0)
		g = g_tick()

		start = time.clock()
		#print(id_spi_to_run)
		while (start - time.clock() + Time_meas > 0):
			time.sleep(next(g))

			if not Worker.check_running():
				break

			for i,k in enumerate(coefs):
			# for i in range(spi_count*cs_count):\
				# print(i)
				input_queue.put(id_spi_to_run[i])
				input_queue.put(function(id_spi_to_run[i]))
				input_queue.put(coefs[i])
				# time.sleep(0.2)
				# print('inputting in cycle, iter,', i)
			input_queue.put(None)
			input_queue.put(None)
			input_queue.put(None)
			Num_iter += 1                                               # DEBUG: Count number of iteration
			# yield  # Добавить Num_iter, чтобы ловить итерации 
		print('    Time_meas =', Time_meas)
		print('    Freq meas =', Num_iter/Time_meas)    

class WorkerSignals(QObject):
	'''
	Defines the signals available from a running worker thread.

	Supported signals are:

	finished
		No data

	error
		`tuple` (exctype, value, traceback.format_exc() )

	result
		`object` data returned from processing, anything

	process
		`int` indicating % process

	'''
	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	process = pyqtSignal(int)

	# stop = pyqtSignal(bool)


class Worker(QRunnable):
	'''
	Worker thread

	Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

	:param callback: The function callback to run on this worker thread. Supplied args and 
					 kwargs will be passed through to the runner.
	:type callback: function
	:param args: Arguments to pass to the callback function
	:param kwargs: Keywords to pass to the callback function

	'''

	def __init__(self, fn, *args, **kwargs):
		super(Worker, self).__init__()

		# Store constructor arguments (re-used for processing)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()
		self.running_state = True

		# Add the callback to our kwargs
		self.kwargs['Worker'] = self
		# print(kwargs)
		self.kwargs['process_callback'] = self.signals.process
		# print(kwargs)
		# self.kwargs['running'] = self.signals.stop

	# def __del__(self):
	#     print('del for QRunnable was called')

	@pyqtSlot()
	def run(self):
		'''
		Initialise the runner function with passed args, kwargs.
		'''

		# Retrieve args/kwargs here; and fire processing using them
		try:
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.finished.emit()  # Done

	# @pyqtSlot()
	# def started(self, fnc):
	#     fnc()

	# def stop_t(self):    
	#     self.kwargs['flag'] = False

	def check_running(self):
		# self.fn(*self.args, **self.kwargs)
		# print(self.kwargs['flag'])
		# self.kwargs['flag'] = False
		# print(self.kwargs['flag'])
		# print('check stop called')
		return self.running_state



class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(722, 802)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
		MainWindow.setSizePolicy(sizePolicy)
		MainWindow.setBaseSize(QtCore.QSize(10, 0))
		font = QtGui.QFont()
		font.setPointSize(9)
		MainWindow.setFont(font)
		MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout_5 = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout_5.setObjectName("gridLayout_5")
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setObjectName("gridLayout")
		self.label_1 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_1.sizePolicy().hasHeightForWidth())
		self.label_1.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_1.setFont(font)
		self.label_1.setObjectName("label_1")
		self.gridLayout.addWidget(self.label_1, 0, 0, 2, 1)
		self.pushButton_1_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_1_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_1_MMA.setSizePolicy(sizePolicy)
		self.pushButton_1_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_1_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_1_MMA.setFont(font)
		self.pushButton_1_MMA.setObjectName("pushButton_1_MMA")
		self.gridLayout.addWidget(self.pushButton_1_MMA, 0, 2, 1, 1)
		self.lineEdit_1_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_1_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_1_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_1_MMG_coeff.setObjectName("lineEdit_1_MMG_coeff")
		self.gridLayout.addWidget(self.lineEdit_1_MMG_coeff, 1, 3, 1, 1)
		self.pushButton_1_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_1_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_1_MMG.setSizePolicy(sizePolicy)
		self.pushButton_1_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_1_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_1_MMG.setFont(font)
		self.pushButton_1_MMG.setObjectName("pushButton_1_MMG")
		self.gridLayout.addWidget(self.pushButton_1_MMG, 0, 3, 1, 1)
		self.lineEdit_1_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_1_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_1_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_1_MMA_coeff.setObjectName("lineEdit_1_MMA_coeff")
		self.gridLayout.addWidget(self.lineEdit_1_MMA_coeff, 1, 2, 1, 1)
		self.label = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
		self.label.setSizePolicy(sizePolicy)
		self.label.setObjectName("label")
		self.gridLayout.addWidget(self.label, 1, 1, 1, 1)
		self.gridLayout_11 = QtWidgets.QGridLayout()
		self.gridLayout_11.setObjectName("gridLayout_11")
		self.gridLayout.addLayout(self.gridLayout_11, 0, 4, 2, 1)
		self.gridLayout.setColumnStretch(0, 1)
		self.gridLayout.setColumnStretch(1, 1)
		self.gridLayout.setColumnStretch(2, 2)
		self.gridLayout.setColumnStretch(3, 2)
		self.gridLayout.setColumnStretch(4, 23)
		self.gridLayout_5.addLayout(self.gridLayout, 3, 0, 1, 2)
		self.gridLayout_4 = QtWidgets.QGridLayout()
		self.gridLayout_4.setObjectName("gridLayout_4")
		self.lineEdit_2_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_2_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_2_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_2_MMG_coeff.setObjectName("lineEdit_2_MMG_coeff")
		self.gridLayout_4.addWidget(self.lineEdit_2_MMG_coeff, 1, 3, 1, 1)
		self.label_7 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
		self.label_7.setSizePolicy(sizePolicy)
		self.label_7.setObjectName("label_7")
		self.gridLayout_4.addWidget(self.label_7, 1, 1, 1, 1)
		self.lineEdit_2_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_2_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_2_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_2_MMA_coeff.setObjectName("lineEdit_2_MMA_coeff")
		self.gridLayout_4.addWidget(self.lineEdit_2_MMA_coeff, 1, 2, 1, 1)
		self.label_2 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
		self.label_2.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_2.setFont(font)
		self.label_2.setObjectName("label_2")
		self.gridLayout_4.addWidget(self.label_2, 0, 0, 2, 1)
		self.pushButton_2_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_2_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_2_MMA.setSizePolicy(sizePolicy)
		self.pushButton_2_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_2_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_2_MMA.setFont(font)
		self.pushButton_2_MMA.setObjectName("pushButton_2_MMA")
		self.gridLayout_4.addWidget(self.pushButton_2_MMA, 0, 2, 1, 1)
		self.pushButton_2_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_2_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_2_MMG.setSizePolicy(sizePolicy)
		self.pushButton_2_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_2_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_2_MMG.setFont(font)
		self.pushButton_2_MMG.setObjectName("pushButton_2_MMG")
		self.gridLayout_4.addWidget(self.pushButton_2_MMG, 0, 3, 1, 1)
		self.gridLayout_12 = QtWidgets.QGridLayout()
		self.gridLayout_12.setObjectName("gridLayout_12")
		self.gridLayout_4.addLayout(self.gridLayout_12, 0, 4, 2, 1)
		self.gridLayout_4.setColumnStretch(0, 1)
		self.gridLayout_5.addLayout(self.gridLayout_4, 4, 0, 1, 2)
		self.gridLayout_3 = QtWidgets.QGridLayout()
		self.gridLayout_3.setObjectName("gridLayout_3")
		self.gridLayout_9 = QtWidgets.QGridLayout()
		self.gridLayout_9.setObjectName("gridLayout_9")
		self.lineEdit_filename = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_filename.sizePolicy().hasHeightForWidth())
		self.lineEdit_filename.setSizePolicy(sizePolicy)
		self.lineEdit_filename.setMinimumSize(QtCore.QSize(0, 0))
		self.lineEdit_filename.setObjectName("lineEdit_filename")
		self.gridLayout_9.addWidget(self.lineEdit_filename, 1, 0, 1, 2)
		self.PushButton_Start = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.PushButton_Start.sizePolicy().hasHeightForWidth())
		self.PushButton_Start.setSizePolicy(sizePolicy)
		self.PushButton_Start.setObjectName("PushButton_Start")
		self.gridLayout_9.addWidget(self.PushButton_Start, 0, 0, 1, 1)
		self.PushButton_Stop = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.PushButton_Stop.sizePolicy().hasHeightForWidth())
		self.PushButton_Stop.setSizePolicy(sizePolicy)
		self.PushButton_Stop.setObjectName("PushButton_Stop")
		self.gridLayout_9.addWidget(self.PushButton_Stop, 0, 1, 1, 1)
		spacerItem = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout_9.addItem(spacerItem, 2, 2, 1, 1)
		self.gridLayout_3.addLayout(self.gridLayout_9, 0, 0, 1, 1)
		spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout_3.addItem(spacerItem1, 0, 2, 1, 1)
		self.gridLayout_17 = QtWidgets.QGridLayout()
		self.gridLayout_17.setObjectName("gridLayout_17")
		self.gridLayout_19 = QtWidgets.QGridLayout()
		self.gridLayout_19.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
		self.gridLayout_19.setObjectName("gridLayout_19")
		self.pushButton_cs5 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs5.sizePolicy().hasHeightForWidth())
		self.pushButton_cs5.setSizePolicy(sizePolicy)
		self.pushButton_cs5.setCheckable(True)
		self.pushButton_cs5.setObjectName("pushButton_cs5")
		self.gridLayout_19.addWidget(self.pushButton_cs5, 1, 2, 1, 1)
		self.pushButton_cs3 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs3.sizePolicy().hasHeightForWidth())
		self.pushButton_cs3.setSizePolicy(sizePolicy)
		self.pushButton_cs3.setCheckable(True)
		self.pushButton_cs3.setObjectName("pushButton_cs3")
		self.gridLayout_19.addWidget(self.pushButton_cs3, 0, 3, 1, 1)
		self.pushButton_cs6 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs6.sizePolicy().hasHeightForWidth())
		self.pushButton_cs6.setSizePolicy(sizePolicy)
		self.pushButton_cs6.setCheckable(True)
		self.pushButton_cs6.setObjectName("pushButton_cs6")
		self.gridLayout_19.addWidget(self.pushButton_cs6, 1, 3, 1, 1)
		self.pushButton_cs2 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs2.sizePolicy().hasHeightForWidth())
		self.pushButton_cs2.setSizePolicy(sizePolicy)
		self.pushButton_cs2.setCheckable(True)
		self.pushButton_cs2.setObjectName("pushButton_cs2")
		self.gridLayout_19.addWidget(self.pushButton_cs2, 0, 2, 1, 1)
		self.pushButton_cs1 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs1.sizePolicy().hasHeightForWidth())
		self.pushButton_cs1.setSizePolicy(sizePolicy)
		self.pushButton_cs1.setCheckable(True)
		self.pushButton_cs1.setObjectName("pushButton_cs1")
		self.gridLayout_19.addWidget(self.pushButton_cs1, 0, 1, 1, 1)
		self.pushButton_cs4 = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_cs4.sizePolicy().hasHeightForWidth())
		self.pushButton_cs4.setSizePolicy(sizePolicy)
		self.pushButton_cs4.setCheckable(True)
		self.pushButton_cs4.setObjectName("pushButton_cs4")
		self.gridLayout_19.addWidget(self.pushButton_cs4, 1, 1, 1, 1)
		self.label_13 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
		self.label_13.setSizePolicy(sizePolicy)
		self.label_13.setMinimumSize(QtCore.QSize(0, 28))
		font = QtGui.QFont()
		font.setPointSize(10)
		font.setBold(False)
		font.setWeight(50)
		self.label_13.setFont(font)
		self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.label_13.setObjectName("label_13")
		self.gridLayout_19.addWidget(self.label_13, 1, 0, 1, 1)
		self.label_12 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
		self.label_12.setSizePolicy(sizePolicy)
		self.label_12.setMinimumSize(QtCore.QSize(0, 28))
		font = QtGui.QFont()
		font.setPointSize(10)
		font.setBold(False)
		font.setWeight(50)
		self.label_12.setFont(font)
		self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.label_12.setObjectName("label_12")
		self.gridLayout_19.addWidget(self.label_12, 0, 0, 1, 1)
		spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout_19.addItem(spacerItem2, 2, 1, 1, 3)
		self.gridLayout_19.setColumnMinimumWidth(0, 30)
		self.gridLayout_19.setColumnMinimumWidth(1, 30)
		self.gridLayout_19.setColumnMinimumWidth(2, 30)
		self.gridLayout_19.setColumnMinimumWidth(3, 30)
		self.gridLayout_17.addLayout(self.gridLayout_19, 0, 1, 1, 1)
		self.gridLayout_18 = QtWidgets.QGridLayout()
		self.gridLayout_18.setContentsMargins(-1, -1, 0, -1)
		self.gridLayout_18.setObjectName("gridLayout_18")
		self.label_spi_freq = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_spi_freq.sizePolicy().hasHeightForWidth())
		self.label_spi_freq.setSizePolicy(sizePolicy)
		self.label_spi_freq.setMinimumSize(QtCore.QSize(0, 24))
		self.label_spi_freq.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.label_spi_freq.setObjectName("label_spi_freq")
		self.gridLayout_18.addWidget(self.label_spi_freq, 2, 0, 1, 1)
		self.lineEdit_measFreq = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_measFreq.sizePolicy().hasHeightForWidth())
		self.lineEdit_measFreq.setSizePolicy(sizePolicy)
		self.lineEdit_measFreq.setObjectName("lineEdit_measFreq")
		self.gridLayout_18.addWidget(self.lineEdit_measFreq, 1, 1, 1, 1)
		self.lineEdit_spiFreq = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_spiFreq.sizePolicy().hasHeightForWidth())
		self.lineEdit_spiFreq.setSizePolicy(sizePolicy)
		self.lineEdit_spiFreq.setObjectName("lineEdit_spiFreq")
		self.gridLayout_18.addWidget(self.lineEdit_spiFreq, 2, 1, 1, 1)
		self.label_cs = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_cs.sizePolicy().hasHeightForWidth())
		self.label_cs.setSizePolicy(sizePolicy)
		self.label_cs.setMinimumSize(QtCore.QSize(0, 24))
		self.label_cs.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.label_cs.setObjectName("label_cs")
		self.gridLayout_18.addWidget(self.label_cs, 1, 0, 1, 1)
		self.label_Timemeas = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_Timemeas.sizePolicy().hasHeightForWidth())
		self.label_Timemeas.setSizePolicy(sizePolicy)
		self.label_Timemeas.setMinimumSize(QtCore.QSize(24, 0))
		self.label_Timemeas.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.label_Timemeas.setObjectName("label_Timemeas")
		self.gridLayout_18.addWidget(self.label_Timemeas, 0, 0, 1, 1)
		self.lineEdit_Timemeas = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_Timemeas.sizePolicy().hasHeightForWidth())
		self.lineEdit_Timemeas.setSizePolicy(sizePolicy)
		self.lineEdit_Timemeas.setObjectName("lineEdit_Timemeas")
		self.gridLayout_18.addWidget(self.lineEdit_Timemeas, 0, 1, 1, 1)
		self.gridLayout_17.addLayout(self.gridLayout_18, 0, 0, 1, 1)
		self.gridLayout_3.addLayout(self.gridLayout_17, 0, 1, 1, 1)
		self.gridLayout_3.setColumnStretch(0, 1)
		self.gridLayout_5.addLayout(self.gridLayout_3, 0, 0, 1, 2)
		self.gridLayout_7 = QtWidgets.QGridLayout()
		self.gridLayout_7.setObjectName("gridLayout_7")
		self.pushButton_4_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_4_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_4_MMA.setSizePolicy(sizePolicy)
		self.pushButton_4_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_4_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_4_MMA.setFont(font)
		self.pushButton_4_MMA.setObjectName("pushButton_4_MMA")
		self.gridLayout_7.addWidget(self.pushButton_4_MMA, 0, 2, 1, 1)
		self.lineEdit_4_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_4_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_4_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_4_MMG_coeff.setObjectName("lineEdit_4_MMG_coeff")
		self.gridLayout_7.addWidget(self.lineEdit_4_MMG_coeff, 1, 3, 1, 1)
		self.label_9 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
		self.label_9.setSizePolicy(sizePolicy)
		self.label_9.setObjectName("label_9")
		self.gridLayout_7.addWidget(self.label_9, 1, 1, 1, 1)
		self.label_4 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
		self.label_4.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_4.setFont(font)
		self.label_4.setObjectName("label_4")
		self.gridLayout_7.addWidget(self.label_4, 0, 0, 2, 1)
		self.lineEdit_4_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_4_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_4_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_4_MMA_coeff.setObjectName("lineEdit_4_MMA_coeff")
		self.gridLayout_7.addWidget(self.lineEdit_4_MMA_coeff, 1, 2, 1, 1)
		self.pushButton_4_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_4_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_4_MMG.setSizePolicy(sizePolicy)
		self.pushButton_4_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_4_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_4_MMG.setFont(font)
		self.pushButton_4_MMG.setObjectName("pushButton_4_MMG")
		self.gridLayout_7.addWidget(self.pushButton_4_MMG, 0, 3, 1, 1)
		self.gridLayout_14 = QtWidgets.QGridLayout()
		self.gridLayout_14.setObjectName("gridLayout_14")
		self.gridLayout_7.addLayout(self.gridLayout_14, 0, 4, 2, 1)
		self.gridLayout_7.setColumnStretch(0, 1)
		self.gridLayout_7.setColumnStretch(1, 1)
		self.gridLayout_7.setColumnStretch(2, 2)
		self.gridLayout_7.setColumnStretch(3, 2)
		self.gridLayout_7.setColumnStretch(4, 23)
		self.gridLayout_5.addLayout(self.gridLayout_7, 6, 0, 1, 1)
		self.gridLayout_6 = QtWidgets.QGridLayout()
		self.gridLayout_6.setObjectName("gridLayout_6")
		self.pushButton_3_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_3_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_3_MMG.setSizePolicy(sizePolicy)
		self.pushButton_3_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_3_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_3_MMG.setFont(font)
		self.pushButton_3_MMG.setObjectName("pushButton_3_MMG")
		self.gridLayout_6.addWidget(self.pushButton_3_MMG, 0, 3, 1, 1)
		self.pushButton_3_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_3_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_3_MMA.setSizePolicy(sizePolicy)
		self.pushButton_3_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_3_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_3_MMA.setFont(font)
		self.pushButton_3_MMA.setObjectName("pushButton_3_MMA")
		self.gridLayout_6.addWidget(self.pushButton_3_MMA, 0, 2, 1, 1)
		self.lineEdit_3_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_3_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_3_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_3_MMA_coeff.setObjectName("lineEdit_3_MMA_coeff")
		self.gridLayout_6.addWidget(self.lineEdit_3_MMA_coeff, 1, 2, 1, 1)
		self.label_8 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
		self.label_8.setSizePolicy(sizePolicy)
		self.label_8.setObjectName("label_8")
		self.gridLayout_6.addWidget(self.label_8, 1, 1, 1, 1)
		self.lineEdit_3_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_3_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_3_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_3_MMG_coeff.setObjectName("lineEdit_3_MMG_coeff")
		self.gridLayout_6.addWidget(self.lineEdit_3_MMG_coeff, 1, 3, 1, 1)
		self.label_3 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
		self.label_3.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_3.setFont(font)
		self.label_3.setObjectName("label_3")
		self.gridLayout_6.addWidget(self.label_3, 0, 0, 2, 1)
		self.gridLayout_13 = QtWidgets.QGridLayout()
		self.gridLayout_13.setObjectName("gridLayout_13")
		self.gridLayout_6.addLayout(self.gridLayout_13, 0, 4, 2, 1)
		self.gridLayout_6.setColumnStretch(0, 1)
		self.gridLayout_6.setColumnStretch(1, 1)
		self.gridLayout_6.setColumnStretch(2, 2)
		self.gridLayout_6.setColumnStretch(3, 2)
		self.gridLayout_6.setColumnStretch(4, 23)
		self.gridLayout_5.addLayout(self.gridLayout_6, 5, 0, 1, 1)
		self.gridLayout_10 = QtWidgets.QGridLayout()
		self.gridLayout_10.setObjectName("gridLayout_10")
		self.label_11 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
		self.label_11.setSizePolicy(sizePolicy)
		self.label_11.setObjectName("label_11")
		self.gridLayout_10.addWidget(self.label_11, 1, 1, 1, 1)
		self.lineEdit_6_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_6_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_6_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_6_MMG_coeff.setObjectName("lineEdit_6_MMG_coeff")
		self.gridLayout_10.addWidget(self.lineEdit_6_MMG_coeff, 1, 3, 1, 1)
		self.label_6 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
		self.label_6.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_6.setFont(font)
		self.label_6.setObjectName("label_6")
		self.gridLayout_10.addWidget(self.label_6, 0, 0, 2, 1)
		self.lineEdit_6_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_6_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_6_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_6_MMA_coeff.setObjectName("lineEdit_6_MMA_coeff")
		self.gridLayout_10.addWidget(self.lineEdit_6_MMA_coeff, 1, 2, 1, 1)
		self.pushButton_6_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_6_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_6_MMA.setSizePolicy(sizePolicy)
		self.pushButton_6_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_6_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_6_MMA.setFont(font)
		self.pushButton_6_MMA.setObjectName("pushButton_6_MMA")
		self.gridLayout_10.addWidget(self.pushButton_6_MMA, 0, 2, 1, 1)
		self.pushButton_6_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_6_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_6_MMG.setSizePolicy(sizePolicy)
		self.pushButton_6_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_6_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_6_MMG.setFont(font)
		self.pushButton_6_MMG.setObjectName("pushButton_6_MMG")
		self.gridLayout_10.addWidget(self.pushButton_6_MMG, 0, 3, 1, 1)
		self.gridLayout_16 = QtWidgets.QGridLayout()
		self.gridLayout_16.setObjectName("gridLayout_16")
		self.gridLayout_10.addLayout(self.gridLayout_16, 0, 4, 2, 1)
		self.gridLayout_10.setColumnStretch(0, 1)
		self.gridLayout_5.addLayout(self.gridLayout_10, 8, 0, 1, 1)
		self.gridLayout_8 = QtWidgets.QGridLayout()
		self.gridLayout_8.setObjectName("gridLayout_8")
		self.pushButton_5_MMG = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_5_MMG.sizePolicy().hasHeightForWidth())
		self.pushButton_5_MMG.setSizePolicy(sizePolicy)
		self.pushButton_5_MMG.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_5_MMG.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_5_MMG.setFont(font)
		self.pushButton_5_MMG.setObjectName("pushButton_5_MMG")
		self.gridLayout_8.addWidget(self.pushButton_5_MMG, 0, 3, 1, 1)
		self.lineEdit_5_MMG_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_5_MMG_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_5_MMG_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_5_MMG_coeff.setObjectName("lineEdit_5_MMG_coeff")
		self.gridLayout_8.addWidget(self.lineEdit_5_MMG_coeff, 1, 3, 1, 1)
		self.lineEdit_5_MMA_coeff = QtWidgets.QLineEdit(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.lineEdit_5_MMA_coeff.sizePolicy().hasHeightForWidth())
		self.lineEdit_5_MMA_coeff.setSizePolicy(sizePolicy)
		self.lineEdit_5_MMA_coeff.setObjectName("lineEdit_5_MMA_coeff")
		self.gridLayout_8.addWidget(self.lineEdit_5_MMA_coeff, 1, 2, 1, 1)
		self.label_5 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
		self.label_5.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.label_5.setFont(font)
		self.label_5.setObjectName("label_5")
		self.gridLayout_8.addWidget(self.label_5, 0, 0, 2, 1)
		self.label_10 = QtWidgets.QLabel(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
		self.label_10.setSizePolicy(sizePolicy)
		self.label_10.setObjectName("label_10")
		self.gridLayout_8.addWidget(self.label_10, 1, 1, 1, 1)
		self.pushButton_5_MMA = QtWidgets.QPushButton(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.pushButton_5_MMA.sizePolicy().hasHeightForWidth())
		self.pushButton_5_MMA.setSizePolicy(sizePolicy)
		self.pushButton_5_MMA.setMinimumSize(QtCore.QSize(40, 0))
		self.pushButton_5_MMA.setMaximumSize(QtCore.QSize(40, 16777215))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.pushButton_5_MMA.setFont(font)
		self.pushButton_5_MMA.setObjectName("pushButton_5_MMA")
		self.gridLayout_8.addWidget(self.pushButton_5_MMA, 0, 2, 1, 1)
		self.gridLayout_15 = QtWidgets.QGridLayout()
		self.gridLayout_15.setObjectName("gridLayout_15")
		self.gridLayout_8.addLayout(self.gridLayout_15, 0, 4, 2, 1)
		self.gridLayout_8.setColumnStretch(0, 1)
		self.gridLayout_8.setColumnStretch(1, 1)
		self.gridLayout_8.setColumnStretch(2, 2)
		self.gridLayout_8.setColumnStretch(3, 2)
		self.gridLayout_8.setColumnStretch(4, 23)
		self.gridLayout_5.addLayout(self.gridLayout_8, 7, 0, 1, 1)
		self.gridLayout_2 = QtWidgets.QGridLayout()
		self.gridLayout_2.setObjectName("gridLayout_2")
		self.pushButton_ResetDefaults = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_ResetDefaults.setObjectName("pushButton_ResetDefaults")
		self.gridLayout_2.addWidget(self.pushButton_ResetDefaults, 0, 0, 1, 1)
		spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout_2.addItem(spacerItem3, 0, 1, 1, 1)
		self.gridLayout_5.addLayout(self.gridLayout_2, 9, 0, 1, 1)
		spacerItem4 = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.gridLayout_5.addItem(spacerItem4, 10, 0, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 722, 26))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.label_1.setText(_translate("MainWindow", "1:"))
		self.pushButton_1_MMA.setText(_translate("MainWindow", "MMA"))
		self.pushButton_1_MMG.setText(_translate("MainWindow", "MMG"))
		self.label.setText(_translate("MainWindow", "coef."))
		self.label_7.setText(_translate("MainWindow", "coef."))
		self.label_2.setText(_translate("MainWindow", "2:"))
		self.pushButton_2_MMA.setText(_translate("MainWindow", "MMA"))
		self.pushButton_2_MMG.setText(_translate("MainWindow", "MMG"))
		self.PushButton_Start.setText(_translate("MainWindow", "Start"))
		self.PushButton_Stop.setText(_translate("MainWindow", "Stop"))
		self.pushButton_cs5.setText(_translate("MainWindow", "5"))
		self.pushButton_cs3.setText(_translate("MainWindow", "3"))
		self.pushButton_cs6.setText(_translate("MainWindow", "6"))
		self.pushButton_cs2.setText(_translate("MainWindow", "2"))
		self.pushButton_cs1.setText(_translate("MainWindow", "1"))
		self.pushButton_cs4.setText(_translate("MainWindow", "4"))
		self.label_13.setText(_translate("MainWindow", "B:"))
		self.label_12.setText(_translate("MainWindow", "A:"))
		self.label_spi_freq.setText(_translate("MainWindow", "SPI Frequency"))
		self.label_cs.setText(_translate("MainWindow", "Measurement Frequency"))
		self.label_Timemeas.setText(_translate("MainWindow", "Time measurement"))
		self.pushButton_4_MMA.setText(_translate("MainWindow", "MMA"))
		self.label_9.setText(_translate("MainWindow", "coef."))
		self.label_4.setText(_translate("MainWindow", "4:"))
		self.pushButton_4_MMG.setText(_translate("MainWindow", "MMG"))
		self.pushButton_3_MMG.setText(_translate("MainWindow", "MMG"))
		self.pushButton_3_MMA.setText(_translate("MainWindow", "MMA"))
		self.label_8.setText(_translate("MainWindow", "coef."))
		self.label_3.setText(_translate("MainWindow", "3:"))
		self.label_11.setText(_translate("MainWindow", "coef."))
		self.label_6.setText(_translate("MainWindow", "6:"))
		self.pushButton_6_MMA.setText(_translate("MainWindow", "MMA"))
		self.pushButton_6_MMG.setText(_translate("MainWindow", "MMG"))
		self.pushButton_5_MMG.setText(_translate("MainWindow", "MMG"))
		self.label_5.setText(_translate("MainWindow", "5:"))
		self.label_10.setText(_translate("MainWindow", "coef."))
		self.pushButton_5_MMA.setText(_translate("MainWindow", "MMA"))
		self.pushButton_ResetDefaults.setText(_translate("MainWindow", "Reset Defaults"))



		self.bind_button_functions_2()
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	# def retranslateUi(self, MainWindow):
	#   _translate = QtCore.QCoreApplication.translate
	#   MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
	#   self.Start.setText(_translate("MainWindow", "Start"))
	#   self.Stop.setText(_translate("MainWindow", "Stop"))


	class header_init(object):
		onlyDouble = QtGui.QDoubleValidator()

		def __init__(self, MainWindow):
			# line for spiFreq
			self.lineEdit_spiFreq = MainWindow.lineEdit_spiFreq
			self.lineEdit_spiFreq.setValidator(self.onlyDouble)
			self.lineEdit_spiFreq.setText(settings.dic['spi_freq'])

			# line for meas_freq
			self.lineEdit_measFreq = MainWindow.lineEdit_measFreq
			self.lineEdit_measFreq.setValidator(self.onlyDouble)
			self.lineEdit_measFreq.setText(settings.dic['meas_freq'])

			self.lineEdit_Timemeas = MainWindow.lineEdit_Timemeas
			self.lineEdit_Timemeas.setValidator(self.onlyDouble)
			self.lineEdit_Timemeas.setText(settings.dic['Time_meas'])

			# line for meas_freq
			self.lineEdit_filename = MainWindow.lineEdit_filename
			self.lineEdit_filename.setText(settings.dic['file_name'])

			# button for
			MainWindow.pushButton_cs1.setEnabled(True)
			MainWindow.pushButton_cs1.setCheckable(True)
			MainWindow.pushButton_cs1.setChecked(True)


	class plot_box_init(object):
		onlyDouble = QtGui.QDoubleValidator()

		def __init__(self, line_MMA, line_MMG, Button_MMA, Button_MMG, Button_cs, cs):

			self.line_MMA = line_MMA
			self.line_MMA.setValidator(self.onlyDouble)
			self.line_MMA.setText(cs['coef_MMA'])

			# self.line_MMA.setDisabled(True)

			self.line_MMG = line_MMG
			self.line_MMG.setValidator(self.onlyDouble)
			self.line_MMG.setText(cs['coef_MMG'])
			self.line_MMG.setDisabled(True)

			self.Button_cs = Button_cs
			self.Button_cs.setEnabled(True)
			self.Button_cs.setCheckable(True)
			self.Button_cs.setChecked(cs['State'])
			# self.Button_cs.toggle()
			# self.Button_cs.toggled[bool].connect(A_B_buttons.print_hw)

			self.Button_MMA = Button_MMA
			self.Button_MMA.setEnabled(cs['MMA_MMG_flag'])
			self.Button_MMA.setCheckable(True)
			self.Button_MMA.setChecked(True)

			self.Button_MMG = Button_MMG
			self.Button_MMG.setEnabled(not cs['MMA_MMG_flag'])
			self.Button_MMG.setCheckable(True)
			self.Button_MMG.setChecked(True)

			# print(self.Button_MMA.isEnabled())
			# print(self.Button_MMG.isEnabled())
			self.active_state_Button_MMA = self.Button_MMA.isEnabled()
			self.active_state_Button_MMG = self.Button_MMG.isEnabled()

			# self.mma()
			# self.mmg()


			self.freeze()

			self.Button_MMA.clicked.connect(self.mma_on)
			self.Button_MMG.clicked.connect(self.mmg_on)

			# self.Button_MMA.clicked.connect(lambda: self.mma_mmg_swap(Button_pressed=Button_MMG, Button_released=Button_MMA, line_pressed=line_MMG, line_released=line_MMA))
			# self.Button_MMG.clicked.connect(lambda: self.mma_mmg_swap(Button_pressed=Button_MMA, Button_released=Button_MMG, line_pressed=line_MMA, line_released=line_MMG))

			self.line_MMA.textChanged.connect(self.change_coef)
			self.line_MMG.textChanged.connect(self.change_coef)
			# self.Stop.clicked.connect(self.stop)
			self.coef = None

			self.startup_cs_init()

			self.cs_state = self.Button_cs.isChecked()


		def mmg_on(self):
			self.Button_MMA.setEnabled(True)
			self.Button_MMA.setChecked(True)
			self.Button_MMG.setDisabled(True)

			self.active_state_Button_MMA = self.Button_MMA.isEnabled()
			self.active_state_Button_MMG = self.Button_MMG.isEnabled()

			self.line_MMA.setEnabled(True)
			self.line_MMG.setDisabled(True)

			self.coef = self.line_MMA.text()
			# print('mmg')

		def mma_on(self):
			# Используется при нажатии на кнопку ММА, выключает
			self.Button_MMG.setEnabled(True)
			self.Button_MMG.setChecked(True)
			self.Button_MMA.setDisabled(True)

			self.active_state_Button_MMA = self.Button_MMA.isEnabled()
			self.active_state_Button_MMG = self.Button_MMG.isEnabled()

			self.line_MMG.setEnabled(True)
			self.line_MMA.setDisabled(True)
			
			self.coef = self.line_MMG.text()
			# print('mma')

		def startup_cs_init(self):
			# узнает, включен ли cs при старте
			if self.Button_cs.isChecked():
				# print('MainWindow.pushButton_cs1.isChecked()')
				self.unfreeze()
				self.cs_state = self.Button_cs.isChecked()

		def freeze(self):
			# выключает поле с графиком и кнопками выбора ММА ММГ
			self.Button_MMA.setDisabled(True)
			self.Button_MMG.setDisabled(True)
			self.line_MMA.setDisabled(True)
			self.line_MMG.setDisabled(True)

		def unfreeze(self):
			# возвращает поле из freeze в обратное состояние
			if self.active_state_Button_MMA:
				self.Button_MMA.setEnabled(True)
				self.line_MMA.setEnabled(True)

				self.coef = self.line_MMA.text()
				# print(self.coef)

			if self.active_state_Button_MMG:
				self.Button_MMG.setEnabled(True)
				self.line_MMG.setEnabled(True)

				self.coef = self.line_MMG.text()
				# print(self.coef)


		# def set_coef(self):
		#   if self.active_state_Button_MMA:
		#       self.coef = self.line_MMA.text()
		#       print(self.coef)

		#   if self.active_state_Button_MMG:
		#       self.coef = self.line_MMG.text()
		#       print(self.coef)

		def change_coef(self, text):
			# Изменяет коэффициент, при изменении текстового поля (либо для ММА введенное, либо для ММГ)
			if self.active_state_Button_MMA:
				self.coef = text
				# print(self.coef)

			if self.active_state_Button_MMG:
				self.coef = text
				# print(self.coef)


		def add_cs(self, pressed):
			# блокирует/разблокирует каналы, при нажатии
			if pressed:
				# bisect.insort(chosen_cs, 1)
				# self.change_coef()
				# bisect.insort(chosen_cs, 1)
				self.unfreeze()
				self.cs_state = self.Button_cs.isChecked()
				# print(chosen_cs)
				# print('add')
			else:
				# chosen_cs.remove(1)
				self.freeze()
				self.cs_state = self.Button_cs.isChecked()
				# print(chosen_cs)
				# print('remove')

		def get_cs_state(self):
			print(self.cs_state)
			return self.cs_state

		def get_coef(self):
			
			if self.cs_state:
				return self.coef


	def bind_button_functions_2(self):


		self.my_header = self.header_init(MainWindow=self)
	
		
		# global my_plot_box_1
		self.my_plot_box_1 = self.plot_box_init(line_MMA=self.lineEdit_1_MMA_coeff, line_MMG=self.lineEdit_1_MMG_coeff, Button_MMA=self.pushButton_1_MMA, Button_MMG=self.pushButton_1_MMG, Button_cs=self.pushButton_cs1, cs=settings.cs_1)
		self.my_plot_box_2 = self.plot_box_init(line_MMA=self.lineEdit_2_MMA_coeff, line_MMG=self.lineEdit_2_MMG_coeff, Button_MMA=self.pushButton_2_MMA, Button_MMG=self.pushButton_2_MMG, Button_cs=self.pushButton_cs2, cs=settings.cs_2)
		self.my_plot_box_3 = self.plot_box_init(line_MMA=self.lineEdit_3_MMA_coeff, line_MMG=self.lineEdit_3_MMG_coeff, Button_MMA=self.pushButton_3_MMA, Button_MMG=self.pushButton_3_MMG, Button_cs=self.pushButton_cs3, cs=settings.cs_3)
		self.my_plot_box_4 = self.plot_box_init(line_MMA=self.lineEdit_4_MMA_coeff, line_MMG=self.lineEdit_4_MMG_coeff, Button_MMA=self.pushButton_4_MMA, Button_MMG=self.pushButton_4_MMG, Button_cs=self.pushButton_cs4, cs=settings.cs_4)
		self.my_plot_box_5 = self.plot_box_init(line_MMA=self.lineEdit_5_MMA_coeff, line_MMG=self.lineEdit_5_MMG_coeff, Button_MMA=self.pushButton_5_MMA, Button_MMG=self.pushButton_5_MMG, Button_cs=self.pushButton_cs5, cs=settings.cs_5)
		self.my_plot_box_6 = self.plot_box_init(line_MMA=self.lineEdit_6_MMA_coeff, line_MMG=self.lineEdit_6_MMG_coeff, Button_MMA=self.pushButton_6_MMA, Button_MMG=self.pushButton_6_MMG, Button_cs=self.pushButton_cs6, cs=settings.cs_6)


		self.plot_boxes = [self.my_plot_box_1, self.my_plot_box_2, self.my_plot_box_3, self.my_plot_box_4, self.my_plot_box_5, self.my_plot_box_6]


		self.pushButton_cs1.clicked[bool].connect(self.my_plot_box_1.add_cs)
		self.pushButton_cs2.clicked[bool].connect(self.my_plot_box_2.add_cs)
		self.pushButton_cs3.clicked[bool].connect(self.my_plot_box_3.add_cs)
		self.pushButton_cs4.clicked[bool].connect(self.my_plot_box_4.add_cs)
		self.pushButton_cs5.clicked[bool].connect(self.my_plot_box_5.add_cs)
		self.pushButton_cs6.clicked[bool].connect(self.my_plot_box_6.add_cs)


		self.PushButton_Start.clicked.connect(self.start)
		self.PushButton_Stop.clicked.connect(self.stop)
		self.pushButton_ResetDefaults.clicked.connect(settings.rewrite)


		self.lineEdit_1_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_1_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_2_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_2_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_3_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_3_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_4_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_4_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_5_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_5_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_6_MMA_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.lineEdit_6_MMG_coeff.setFocusPolicy(QtCore.Qt.ClickFocus)


		self.lineEdit_filename.textChanged.connect(set_file_name)
		self.lineEdit_measFreq.textChanged.connect(set_meas_freq)
		self.lineEdit_Timemeas.textChanged.connect(set_time_meas)
		self.lineEdit_spiFreq.textChanged.connect(set_spi_freq)


		self.graphicsView1 = Window()
		self.graphicsView2 = Window()
		self.graphicsView3 = Window()
		self.graphicsView4 = Window()
		self.graphicsView5 = Window()
		self.graphicsView6 = Window()
		self.gridLayout_11.addWidget(self.graphicsView1)
		self.gridLayout_12.addWidget(self.graphicsView2)
		self.gridLayout_13.addWidget(self.graphicsView3)
		self.gridLayout_14.addWidget(self.graphicsView4)
		self.gridLayout_15.addWidget(self.graphicsView5)
		self.gridLayout_16.addWidget(self.graphicsView6)



		MainWindow._update()



		self.threadpool = QThreadPool()
		print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

		# установка одного таймера на все графики
		# def set_timer():
		#   self.graphicsView1.update()
		#   self.graphicsView2.update()
		#   self.graphicsView3.update()
		#   self.graphicsView4.update()
		#   self.graphicsView5.update()
		#   self.graphicsView6.update()

		# self.timer = QtCore.QTimer()
		# self.timer.setInterval(50) # in milliseconds
		# self.timer.start()
		# self.timer.timeout.connect(set_timer)
		# print('connecnted')



		# self.ui.lineEdit_1_MMA_coeff.textChanged.connect(self.sync_lineEdit)
		# self.ui.lineEdit_1_MMG_coeff.textChanged.connect(self.sync_lineEdit)
		# my_plot_box_1.mma()
		# self.pushButton_1_MMA.clicked.connect(self.mma)
		# self.pushButton_1_MMG.clicked.connect(self.mmg)


	def start(self):
		global plot_deque
		global stop_flag


		stop_flag = False

		plot_deque = collections.deque([0]*10000, maxlen=10000) #1000

		def print_output(s):
			# print(s)
			pass

		def thread_input_complete():
			self.worker_process.running_state = False
			# self.worker_plot.running_state = False
			# print(self.input_properties)
			self.input_properties.file.close()
			# self.plot_timer.stop()

			self.PushButton_Start.setEnabled(True)
			print("THREAD COMPLETE! input")

		def thread_complete():
			print("THREAD COMPLETE!")
			# del Worker


		global coefs
		coefs = []
		# coefs = [None]*6
		for i,k in enumerate(self.plot_boxes):
			if k.active_state_Button_MMA or k.active_state_Button_MMG:
				coefs.append(k.get_coef())
			if k.active_state_Button_MMA:
				settings.cs_list[i]['coef_MMA'] = k.get_coef()
			if k.active_state_Button_MMG:
				settings.cs_list[i]['coef_MMG'] = k.get_coef()

		print('coefs', coefs)
		
		temp = []
		# print(coefs)
		# c = 0
		# print(len(coefs))
		for i in range(len(coefs)):
			# c = c + 1
			# print(c)
			# print('item')
			if coefs[i] != None:
				# print('item is not None')
				temp.append(float(coefs[i]))

		coefs = temp
		print(coefs)


		try:
			self.stop()
		except NameError:
			print('NameError at stop')


		self.input_properties = input_for_qrunnable_class()
		self.worker_input = Worker(self.input_properties.execute_this_input) # Any other args, kwargs are passed to the run function
		# self.worker_input.started.connect(print_hw)
		self.worker_input.signals.result.connect(print_output)
		self.worker_input.signals.finished.connect(thread_input_complete)
		# self.worker_input.signals.process.connect(process_fn)
		####################
		# self.worker_input_running_flag = True

		# self.worker_2 = Worker(execute_this_fn) # Any other args, kwargs are passed to the run function
		# self.worker_2.signals.result.connect(print_output)
		# self.worker_2.signals.finished.connect(thread_complete)
		# self.worker_2.signals.process.connect(process_fn)
		####################
		# self.worker_2_running_flag = True

		self.worker_process = Worker(self.input_properties.execute_this_process) # Any other args, kwargs are passed to the run function
		self.worker_process.signals.result.connect(print_output)
		self.worker_process.signals.finished.connect(thread_complete)
		# self.worker_input.signals.process.connect(update_plot)


		# self.worker_plot = Worker(self.input_properties.execute_this_plot) # Any other args, kwargs are passed to the run function
		# self.worker_plot.signals.result.connect(print_output)
		# self.worker_plot.signals.finished.connect(thread_complete)
		# self.worker_plot.signals.process.connect(print_output)
		# Execute
		self.threadpool.start(self.worker_input)
		self.threadpool.start(self.worker_process)
		# self.threadpool.start(self.worker_plot)


		


		"""
		Переопределяем обновления через QTimer, и соотв., главный поток GUI
		"""


		# def init_update_plots():
		class execute_plot_timer(object):
			pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]

			plots_to_run = [ui.graphicsView1, ui.graphicsView2, ui.graphicsView3, ui.graphicsView4, ui.graphicsView5, ui.graphicsView6]

			id_plots_to_run = []
			for i,k in enumerate(pushButton_cs):
				# pass
				if k:
					id_plots_to_run.append(i)

			print(id_plots_to_run)

			@classmethod
			def update_plots(cls):
				for i in cls.id_plots_to_run:
					cls.plots_to_run[i].update(list(self.input_properties.plot_deque[i]))

		mytemp = execute_plot_timer()

		# # init_update_plots()
		# self.plot_timer = QtCore.QTimer()
		# # self.plot_timer.setInterval(1000/plot_freq) # in milliseconds
		# self.plot_timer.start(1000/plot_freq)
		# self.plot_timer.timeout.connect(execute_plot_timer.update_plots)
		

		self.PushButton_Start.setDisabled(True)

	def stop(self):
		global stop_flag
		stop_flag = False


		self.PushButton_Start.setEnabled(True)
		try:
			stop_flag = False
			self.worker_input.running_state = False
			self.worker_process.running_state = False
			# self.plot_timer.stop()
			# self.worker_plot.running_state = False

			# self.input_properties.file.close()
			print('stop pressed')

		except NameError:
			pass
		except AttributeError:
			pass



def catch_exceptions(t, val, tb):
	QtWidgets.QMessageBox.critical(None,
								   "An exception was raised",
								   "Exception type: {}".format(t))
	old_hook(t, val, tb)

old_hook = sys.excepthook
sys.excepthook = catch_exceptions
















class App(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(App, self).__init__(parent)

		# class execute_plot_timer():
		# 	pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]

		# 	plots_to_run = [ui.graphicsView1, ui.graphicsView2, ui.graphicsView3, ui.graphicsView4, ui.graphicsView5, ui.graphicsView6]

		# 	id_plots_to_run = []
		# 	for i,k in enumerate(pushButton_cs):
		# 		# pass
		# 		if k:
		# 			id_plots_to_run.append(i)

		# 	print(id_plots_to_run)

		# 	@classmethod
		# 	def update_plots(cls):
		# 		for i in cls.id_plots_to_run:
		# 			cls.plots_to_run[i].update(list(self.input_properties.plot_deque[i]))
				# QtCore.QTimer.singleShot(1, cls.update_plots)
				# print(time.clock())




		### Create Gui Elements ###########
		# self.mainbox = QtGui.QWidget()
		# self.setCentralWidget(self.mainbox)
		# self.mainbox.setLayout(QtGui.QVBoxLayout())

		# self.canvas = pg.GraphicsLayoutWidget()
		# self.mainbox.layout().addWidget(self.canvas)

		# self.label = QtGui.QLabel()
		# self.mainbox.layout().addWidget(self.label)

		# #  image plot

		# self.canvas.nextRow()
		# #  line plot
		# self.otherplot = self.canvas.addPlot()
		# self.h2 = self.otherplot.plot(pen='y')


		# #### Set Data  #####################

		# self.x = np.linspace(0,50., num=100)
		# self.X,self.Y = np.meshgrid(self.x,self.x)

		# # self.counter = 0

		# #### Start  #####################
		# self._update()
		# self._update()

		# execute_plot_timer.update_plots()
			# print('smt')


	def _update(self):
		global global_flag
		global stop_flag

		if global_flag:
			self.pushButton_cs = [ui.pushButton_cs1.isChecked(), ui.pushButton_cs2.isChecked(), ui.pushButton_cs3.isChecked(), ui.pushButton_cs4.isChecked(), ui.pushButton_cs5.isChecked(), ui.pushButton_cs6.isChecked()]

			self.plots_to_run = [ui.graphicsView1, ui.graphicsView2, ui.graphicsView3, ui.graphicsView4, ui.graphicsView5, ui.graphicsView6]

			self.id_plots_to_run = []
			for i,k in enumerate(self.pushButton_cs):
				# pass
				if k:
					self.id_plots_to_run.append(i)

			print(self.id_plots_to_run)

			global_flag = False

		
		if not global_flag and not stop_flag:
			# print(stop_flag)
			try:
				for i in self.id_plots_to_run:
					self.plots_to_run[i].update(list(ui.input_properties.plot_deque[i]))
			except AttributeError:
				pass


		# for i in ui.mytemp.id_plots_to_run:
		# 	ui.execute_plot_timer.plots_to_run[i].update(list(ui.execute_plot_timer.input_properties.plot_deque[i]))
		
		# self.counter = time.clock()
		# print(self.counter)
		# self.data = np.sin(self.X/3.+self.counter*8)*np.cos(self.Y/3.+self.counter*8)
		# self.ydata = np.sin(self.x/3.+ self.counter*8)

		# self.h2.setData(self.ydata)
		QtCore.QTimer.singleShot(1, self._update)
		# self.counter += 1





if __name__ == "__main__":
	import sys

	global app

	app = QtWidgets.QApplication(sys.argv)
	MainWindow = App()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)

	# gui_response = GuiResponseThreadClass()
	# gui_response.start()

	# my_thread = ThreadClass()
	# my_thread.wait()
	# my_thread.start()
	
	MainWindow.show()



	# threading.Thread(target=my_spi.check_gui).start()
	ret = app.exec_()
	settings.close()
	sys.exit(ret)
