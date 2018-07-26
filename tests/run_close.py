"""
Test to make sure the multiprocessing event loop closes automatically.
"""
import mp_event_loop
import qt_multiprocessing
from qtpy import QtWidgets


class LabelProxy(qt_multiprocessing.WidgetProxy):
    PROXY_CLASS = QtWidgets.QLabel
    GETTERS = ['text']


if __name__ == '__main__':
    loop = qt_multiprocessing.AppEventLoop()
    qt_multiprocessing.WidgetProxy.__loop__ = loop
    loop.start()

    app = QtWidgets.QApplication([])

    lbl = LabelProxy("Hello")

    widg = QtWidgets.QDialog()
    lay = QtWidgets.QFormLayout()
    widg.setLayout(lay)

    # Form
    inp = QtWidgets.QLineEdit()
    btn = QtWidgets.QPushButton('Set Text')
    lay.addRow(inp, btn)

    def set_text():
        lbl.setText(inp.text())

    btn.clicked.connect(set_text)

    widg.show()

    app.exec_()
