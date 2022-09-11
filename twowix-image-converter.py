import sys

from PIL import Image
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pdf2image import convert_from_path
import tempfile
import fitz, os


class ScrollLabel(QScrollArea):
    file_name = []
    status_name = []

    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QGridLayout(content)

        self.file_name_label = QLabel(content)
        self.file_name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.file_name_label.setWordWrap(True)

        self.status_label = QLabel(content)
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.status_label.setWordWrap(True)

        lay.addWidget(self.file_name_label, 0, 0)
        lay.addWidget(self.status_label, 0, 1)

    def reset(self):
        self.file_name = []
        self.status_name = []
        self.file_name_label.setText("\n".join(self.file_name) if len(self.file_name) else "선택된 파일이 없음")
        self.status_label.setText("")

    def set_file(self, file_name, status=None):
        self.file_name.append(file_name)
        self.status_name.append(status)
        tmp_file_name = ""
        for idx, ff in enumerate(self.file_name):
            tmp_file_name += f'{str(idx + 1).zfill(3)}. {ff}\n'
        self.file_name_label.setText(tmp_file_name)
        self.status_label.setText("\n".join(self.status_name))


class Window(QWidget):
    file_list = []
    save_path = None

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon('twowix-logo.png'))
        self.progress = QProgressBar(self)
        self.progress.setGeometry(10, 370, 514, 10)
        self.progress.setFormat("")
        self.progress.setValue(0)

        self.convert_btn = QPushButton('변환', self)
        self.convert_btn.move(430, 10)
        self.convert_btn.resize(60, 40)
        self.convert_btn.clicked.connect(self.convert_file)

        self.compress_btn = QPushButton('압축', self)
        self.compress_btn.move(370, 10)
        self.compress_btn.resize(60, 40)
        self.compress_btn.clicked.connect(self.compress_file)

        self.merge_btn = QPushButton('병합', self)
        self.merge_btn.move(310, 10)
        self.merge_btn.resize(60, 40)
        self.merge_btn.clicked.connect(self.merge_file)

        self.image_upload_btn = QPushButton('파일 가져오기', self)
        self.image_upload_btn.move(10, 10)
        self.image_upload_btn.resize(90, 40)
        self.image_upload_btn.clicked.connect(self.open_file_name_dialog)

        self.save_folder_btn = QPushButton('저장 경로 설정', self)
        self.save_folder_btn.move(100, 10)
        self.save_folder_btn.resize(100, 40)
        self.save_folder_btn.clicked.connect(self.set_save_path)

        self.reset_btn = QPushButton('초기화', self)
        self.reset_btn.move(200, 10)
        self.reset_btn.resize(60, 40)
        self.reset_btn.clicked.connect(self.reset)

        self.save_path_label = QLabel("저장 경로 : 저장경로를 ↑ 설정해주세요.", self)
        self.save_path_label.move(10, 50)
        self.save_path_label.resize(800, 30)

        self.info_label = QLabel(
            "사용법\n"
            "1. 파일 선택 버튼으로 파일 가져오기 (pdf, jpg, png)\n"
            "2. 저장 경로버튼으로 저장할 폴더 선택\n"
            "변환: pdf -> jpg 혹은 png, jpg -> pdf 로 변환\n"
            "압축: pdf, png, jpg -> jpg 로 압축\n"
            "병합: png, jpg -> 하나의 pdf 로 병합",
            self
        )
        self.info_label.move(10, 380)
        self.info_label.resize(800, 100)

        self.made_label = QLabel(self)
        self.made_label.move(70, 440)
        self.made_label.resize(800, 100)
        self.made_label.setText(
            "Made Twowix / twowix@kakao.com / <a href='https://github.com/twowix'>깃허브</a> / <a href='https://twowix.me'>블로그</a> / <a href='https://www.youtube.com/channel/UCjzrt07wES1ZgeTcKtfQCfg'>유튜브</a>")
        self.made_label.setOpenExternalLinks(True)

        self.quit_btn = QPushButton('종료', self)
        self.quit_btn.move(410, 430)
        self.quit_btn.resize(80, 40)
        self.quit_btn.clicked.connect(QCoreApplication.instance().quit)

        self.file_area = ScrollLabel(self)
        self.file_area.reset()
        self.file_area.setGeometry(10, 80, 480, 290)

        self.setWindowTitle('Twowix - Image Converter 0.1.0')
        self.setFixedSize(QSize(500, 505))
        self.center()
        self.show()

    def reset(self):
        self.file_list = []
        self.save_path = ""
        self.progress.setValue(0)
        self.save_path_label.setText("저장 경로 : 저장경로를 ↑ 설정해주세요.")
        self.file_area.reset()
        self.update()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "파일 가져오기",
            "",
            "All Files (*)",
            options=options
        )
        for file_name in file_names:
            ext = file_name.split(".")[-1]
            if ext == "pdf" or ext == "jpg" or ext == "png":
                valid_check = True
                for cur_file in self.file_list:
                    if cur_file["path"] == file_name:
                        valid_check = False
                        break
                if valid_check:
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
            self.progress.setValue(0)
            for idx, file in enumerate(self.file_list):
                self.progress.setValue(int((idx + 1) / len(self.file_list) * 100))
                if file["status"] == "Ready":
                    file["status"] = "Converting..."
                    self.update_label()

                    if file['ext'] == "pdf":
                        self.pdf_convert(file, 'convert')

                    elif file['ext'] == 'jpg' or file['ext'] == 'png':
                        Image.open(file['path']).convert('RGB').save(
                            f"{self.save_path}/convert_{file['name']}.pdf",
                            "PDF"
                        )

                    file["status"] = "Converted"
                    self.update_label()
            QMessageBox.question(self, 'Info', '변환을 완료하였습니다.', QMessageBox.Yes, QMessageBox.NoButton)

    def compress_file(self):
        if not self.save_path:
            QMessageBox.question(self, 'Info', '저장 경로를 설정해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            self.progress.setValue(0)
            for idx, file in enumerate(self.file_list):
                self.progress.setValue(int((idx + 1) / len(self.file_list) * 100))
                if file["status"] == "Ready":
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

    def merge_file(self):
        if not self.save_path:
            QMessageBox.question(self, 'Info', '저장 경로를 설정해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            self.progress.setValue(0)
            first_img = None
            first_img_name = None
            merge_item = []
            for idx, file in enumerate(self.file_list):
                self.progress.setValue(int((idx + 1) / len(self.file_list) * 100))
                if file["status"] == "Ready":
                    file["status"] = "Merging..."
                    self.update_label()

                    if file['ext'] == 'jpg' or file['ext'] == 'png':
                        if first_img:
                            first_img_name = file["name"]
                            merge_item.append(Image.open(file["path"]).convert("RGB"))
                        else:
                            first_img = Image.open(file["path"]).convert("RGB")
                        file["status"] = "Merged"
                    else:
                        file["status"] = "Not Supported"
                    self.update_label()

            if first_img:
                first_img.save(f"{self.save_path}/merge_{first_img_name}.pdf", save_all=True, append_images=merge_item)
            QMessageBox.question(self, 'Info', '병합을 완료하였습니다.', QMessageBox.Yes, QMessageBox.NoButton)

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
        if folder:
            self.save_path = folder
            self.save_path_label.setText(f'Save Path : {self.save_path}')

    def update_label(self):
        self.file_area.reset()
        for idx, file in enumerate(self.file_list):
            self.file_area.set_file(f'{file["name"]}.{file["ext"]}', file["status"])
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
