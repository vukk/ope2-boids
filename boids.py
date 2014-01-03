#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" See engine.py """

import sys
from PySide import QtGui
from engine import Engine

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = Engine()
    sys.exit(app.exec_())

