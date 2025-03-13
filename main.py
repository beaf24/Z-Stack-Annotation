"""
Image Annotator
by Amir Kardoost and Beatriz Fernandes
October 2024
"""

# This Python file uses the following encoding: utf-8
import sys
from PyQt5 import QtWidgets
from Ui_MainWindow import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon1.png"), QtGui.QIcon.Selected, QtGui.QIcon.On)
    MainWindow.setWindowIcon(QtGui.QIcon(icon))
    MainWindow.setWindowTitle("GUI for Annotation")
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
