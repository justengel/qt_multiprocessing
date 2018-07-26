import time

import qt_multiprocessing
from qtpy import QtWidgets


def make_widgets():
    label = QtWidgets.QLabel("hello")
    label.show()
    return {'label': label}


if __name__ == '__main__':
    with qt_multiprocessing.AppEventLoop(initialize_process=make_widgets) as loop:
        app = QtWidgets.QApplication([])

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            loop.add_var_event('label', 'setText', inp.text())

        btn.clicked.connect(set_text)

        widg.show()

        app.exec_()
