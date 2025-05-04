from PyQt5.QtWidgets import QApplication
import sys
from FourBarLinkage_MVC import FourBarLinkage_Controller
from FourBar_GUI import Ui_Form
from PyQt5.QtWidgets import QWidget

class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = FourBarLinkage_Controller(window)
    window.show()
    sys.exit(app.exec_())
