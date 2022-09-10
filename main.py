import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication


class MyApp(QWidget):
    image_type = 'jpg'

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.image_upload_btn = QPushButton('File', self)
        self.image_upload_btn.move(10, 10)
        self.image_upload_btn.resize(80, 40)
        self.image_upload_btn.clicked.connect(self.open_file_name_dialog)

        quit_btn = QPushButton('Quit', self)
        quit_btn.move(400, 150)
        quit_btn.resize(80, 40)
        quit_btn.clicked.connect(QCoreApplication.instance().quit)

        self.setWindowTitle('Twowix - Image Converter (2022-09-10/0.0.3)')
        self.resize(500, 200)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "All Files (*);;Python Files (*.py)", options=options)
        if file_name:
            self.image_type = file_name.split('.')[-1]
            self.information_event()

    def information_event(self):
        if self.image_type == 'jpg':
            convert_dialog = QMessageBox.question(
                self, 'Convert', "Information Message",
                QMessageBox.Yes | QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Reset | QMessageBox.No,
                QMessageBox.No
            )
            if convert_dialog == QMessageBox.Yes:
                print('Yes clicked.')
            elif convert_dialog == QMessageBox.Save:
                print('Save clicked.')
            elif convert_dialog == QMessageBox.Cancel:
                print('Cancel clicked.')
            elif convert_dialog == QMessageBox.Close:
                print('Close clicked.')
            elif convert_dialog == QMessageBox.Reset:
                print('Reply clicked.')
            else:
                print('No clicked.')
        elif self.image_type == 'pdf':
            convert_dialog = QMessageBox.information(
                self, 'Information Title', "Information Message",
                QMessageBox.Yes | QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Reset | QMessageBox.No,
                QMessageBox.No
            )
            if convert_dialog == QMessageBox.Yes:
                print('Yes clicked.')
            elif convert_dialog == QMessageBox.Save:
                print('Save clicked.')
            elif convert_dialog == QMessageBox.Cancel:
                print('Cancel clicked.')
            elif convert_dialog == QMessageBox.Close:
                print('Close clicked.')
            elif convert_dialog == QMessageBox.Reset:
                print('Reply clicked.')
            else:
                print('No clicked.')
        else:
            QMessageBox.information(self, '지원하지 않음', '지원하지 않는 확장자입니다.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
