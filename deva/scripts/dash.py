import sys
import numpy as np
import click
import matplotlib

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvas):

    def __init__(self, xdata, ydata, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.xdata = xdata
        self.ydata = ydata
        self._line = self.axes.plot(self.xdata, self.ydata, 'r')[0]

    def update_line(self, val):
        # Drop off the first y element, append a new one.
        self.ydata = val * np.random.randn(self.xdata.shape[0])
        self._line.set_ydata(self.ydata)
        self.draw()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        n_data = 50
        xdata = np.arange(n_data)
        ydata = np.random.randn(n_data)

        self.canvas = MplCanvas(xdata, ydata, self, width=5, height=4, dpi=100)

        button = QtWidgets.QPushButton("Update")
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(slider)
        layout.addWidget(button)
        container = QtWidgets.QWidget()
        container.setLayout(layout)

        dock = QtWidgets.QDockWidget("Dockable", self)
        dock.setWidget(container)
        self.setCentralWidget(self.canvas)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        button.clicked.connect(lambda: self.canvas.update_line(slider.value()))

        self.show()


@click.command()
def cli():
    app = QtWidgets.QApplication(sys.argv)
    _ = MainWindow()
    app.exec_()
