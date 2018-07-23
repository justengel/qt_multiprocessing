import mp_event_loop
import qt_multiprocessing
from qtpy import QtWidgets


class LabelProxy(qt_multiprocessing.WidgetProxy):
    PROXY_CLASS = QtWidgets.QLabel
    GETTERS = ['text']


if __name__ == '__main__':
    with qt_multiprocessing.AppEventLoop() as loop:
        mp_event_loop.Proxy.__loop__ = loop

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
