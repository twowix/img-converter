import sys

from PIL import Image
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pdf2image import convert_from_path
import tempfile
import fitz, os


class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    # getting text method
    def text(self):
        # getting text of the label
        get_text = self.label.text()

        # return the text
        return get_text


class Window(QWidget):
    file_list = []
    save_path = None

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon('twowix-logo.png'))

        self.convert_btn = QPushButton('변환', self)
        self.convert_btn.move(410, 10)
        self.convert_btn.resize(80, 40)
        self.convert_btn.clicked.connect(self.convert_file)

        self.compress_btn = QPushButton('압축', self)
        self.compress_btn.move(330, 10)
        self.compress_btn.resize(80, 40)
        self.compress_btn.clicked.connect(self.compress_file)

        self.image_upload_btn = QPushButton('파일 가져오기', self)
        self.image_upload_btn.move(10, 10)
        self.image_upload_btn.resize(90, 40)
        self.image_upload_btn.clicked.connect(self.open_file_name_dialog)

        self.save_folder_btn = QPushButton('저장 경로 설정', self)
        self.save_folder_btn.move(100, 10)
        self.save_folder_btn.resize(100, 40)
        self.save_folder_btn.clicked.connect(self.set_save_path)

        self.save_path_label = QLabel("저장 경로 : ", self)
        self.save_path_label.move(10, 50)
        self.save_path_label.resize(800, 30)

        self.info_label = QLabel(
            "사용법\n"
            "1. 파일 선택 버튼으로 파일 가져오기 (pdf, jpg, png)\n"
            "2. 저장 경로버튼으로 저장할 폴더 선택\n"
            "변환: pdf -> jpg / png, jpg -> pdf 로 저장 경로에 변환하여 저장\n"
            "압축: pdf, png, jpg -> jpg 로 압축",
            self
        )
        self.info_label.move(10, 370)
        self.info_label.resize(800, 100)

        self.made_label = QLabel(self)
        self.made_label.move(70, 430)
        self.made_label.resize(800, 100)
        self.made_label.setText(
            "Made Twowix / twowix@kakao.com / <a href='https://github.com/twowix'>깃허브</a> / <a href='https://twowix.me'>블로그</a> / <a href='https://www.youtube.com/channel/UCjzrt07wES1ZgeTcKtfQCfg'>유튜브</a>")
        self.made_label.setOpenExternalLinks(True)

        self.quit_btn = QPushButton('종료', self)
        self.quit_btn.move(410, 415)
        self.quit_btn.resize(80, 40)
        self.quit_btn.clicked.connect(QCoreApplication.instance().quit)

        self.label = ScrollLabel(self)
        self.label.setGeometry(10, 80, 480, 290)

        self.setWindowTitle('Twowix - Image Converter (2022-09-10 / 0.0.1)')
        self.resize(500, 500)
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
        file_names, _ = QFileDialog.getOpenFileNames(self, "파일 가져오기", "",
                                                     "All Files (*)", options=options)
        for file_name in file_names:
            ext = file_name.split(".")[-1]
            if ext == "pdf" or ext == "jpg" or ext == "png":
                self.file_list.append({
                    "path": file_name,
                    "name": file_name.split("/")[-1].replace('.png', '').replace('.jpg', '').replace('.pdf', ''),
                    "ext": file_name.split(".")[-1],
                    "status": "Ready"
                })
            self.update_label()

    def convert_file(self):
        if not self.save_path:
            QMessageBox.question(self, 'Info', '저장 경로를 설정해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            for file in self.file_list:
                file["status"] = "Converting..."
                self.update_label()

                if file['ext'] == "pdf":
                    self.pdf_convert(file, 'convert')

                elif file['ext'] == 'jpg' or file['ext'] == 'png':
                    Image.open(file['path']).save(f"{self.save_path}/convert_{file['name']}.pdf", "PDF")

                file["status"] = "Converted"
                self.update_label()
            QMessageBox.question(self, 'Info', '변환을 완료하였습니다.', QMessageBox.Yes, QMessageBox.NoButton)

    def compress_file(self):
        if not self.save_path:
            QMessageBox.question(self, 'Info', '저장 경로를 설정해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            for file in self.file_list:
                file["status"] = "Compressing..."
                self.update_label()

                if file['ext'] == "pdf":
                    self.pdf_convert(file, 'compress')
                    file["status"] = "Compressed"

                elif file['ext'] == 'jpg' or file['ext'] == 'png':
                    try:
                        Image.open(
                            f"{file['path']}"
                        ).convert('RGB').save(
                            f"{self.save_path}/compress_{file['name']}.jpg",
                            "JPEG"
                        )
                        file["status"] = "Compressed"
                    except Exception as e:
                        file["status"] = "Failed"
                self.update_label()

            QMessageBox.question(self, 'Info', '압축을 완료하였습니다.', QMessageBox.Yes, QMessageBox.NoButton)

    def pdf_convert(self, file, convert_type):
        try:
            mat = fitz.Matrix(2, 2)
            doc = fitz.open(file["path"])

            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                pix.save(f"{self.save_path}/{convert_type}_{file['name']}_{page.number}.png")
                Image.open(
                    f"{self.save_path}/{convert_type}_{file['name']}_{page.number}.png"
                ).convert('RGB').save(
                    f"{self.save_path}/{convert_type}_{file['name']}_{page.number}.jpg",
                    "JPEG"
                )
                os.remove(f"{self.save_path}/{convert_type}_{file['name']}_{page.number}.png")
        except Exception as e:
            print(e)

    def set_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, 'Find Folder')
        self.save_path = folder
        self.save_path_label.setText(f'Save Path : {self.save_path}')

    def update_label(self):
        label_set = ""
        for idx, file in enumerate(self.file_list):
            label_set += f'{idx+1}. {file["name"]} / {file["status"]}\n'
        self.label.setText(label_set)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
