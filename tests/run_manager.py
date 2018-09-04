"""
Test trying to get multiprocessing managers to work with Qt.

There doesn't seem to be a good way of proxying Qt with Managers.
"""
import multiprocessing as mp
import multiprocessing.managers as manage

import mp_event_loop

from qtpy import QtWidgets

import qt_multiprocessing


class QtManager(manage.BaseManager):
    pass


def test_run_1():
    QtManager.register('Label', QtWidgets.QLabel)

    with qt_multiprocessing.AppEventLoop() as loop:
        app = QtWidgets.QApplication([])

        mngr = QtManager()
        mngr.start()

        # Create the proxy label
        lbl = mngr.Label("Hello")  # FAILS HERE
        lbl.show()

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            value = inp.text()
            lbl = mngr.Label("Hello")
            lbl.setText(value)
            # loop.add_var_event('label', 'setText', value)

        btn.clicked.connect(set_text)

        widg.show()

        app.exec_()


def test_run_2():
    with qt_multiprocessing.AppEventLoop() as loop:
        app = QtWidgets.QApplication([])

        QtManager.register('Label', QtWidgets.QLabel)
        mngr = QtManager()
        mngr.start()

        # Create the proxy label
        lbl = mngr.Label("Hello")
        lbl.show()

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            value = inp.text()
            lbl.setText(value)
            # loop.add_var_event('label', 'setText', value)

        btn.clicked.connect(set_text)

        widg.show()

        app.exec_()


def test_run_3():
    with qt_multiprocessing.AppEventLoop() as loop:
        app = QtWidgets.QApplication([])

        QtManager.register('Label', QtWidgets.QLabel)
        mngr = QtManager()
        mngr.start()

        # Create the proxy label
        lbl = mngr.Label("Hello")
        lbl.show()

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            value = inp.text()
            lbl.setText(value)
            # loop.add_var_event('label', 'setText', value)

        btn.clicked.connect(set_text)

        widg.show()

        app.exec_()


if __name__ == '__main__':
    test_run_2()
