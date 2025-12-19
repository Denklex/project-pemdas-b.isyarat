import sys
import os
import subprocess #fungsi penghubung

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QStackedWidget
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import QRect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "gambar")

def img(name):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        print("Gambar tidak ditemukan:", path)
    return path

BG1 = img("halaman 1.png")
BG2 = img("halaman 2.png")
BG3 = img("halaman 3.png")
BG4 = img("halaman 4.png")
BG5 = img("halaman 5.png")
BG6 = img("halaman 6.png")
BG7 = img("halaman 7.png")
BG8 = img("halaman 8.png")

BTN_MASUK = img("halaman 1 tombol masuk.png")

BTN2_PRAKTIK = img("halaman 2 pratik bahasa isyarat.png")
BTN2_TUTORIAL = img("halaman 2 tombol tutorial bahasa isyarat.png")

BTN3_ABJAD = img("halaman 3 tombol abjad.png")
BTN3_ANGKA = img("halaman 3 tombol angka.png")
BTN3_MENU = img("halaman 3 tombol kembali menu.png")
BTN3_KOSAKATA = img("halaman 3 tombol kosakata.png")

BTN4_MENU = img("halaman 4 tombol kembali menu.png")
BTN4_NEXT = img("halaman 4 tombol halaman selanjutnya.png")

BTN5_MENU = img("halaman 5 tombol kembali ke menu.png")
BTN5_PREV = img("halaman 5 tombol sebelumnya.png")
BTN5_NEXT = img("halaman 5 tombol selanjutnya.png")

BTN6_PREV = img("halaman 6 tombol sebelumnya.png")
BTN6_MENU = img("halaman 6 tombol kembali ke menu.png")

BTN7_MENU = img("halaman 7 tombol kembali kemenu.png")
BTN8_MENU = img("halaman 8 tombol kembali ke menu.png")

def find_button_rect(image):
    w = image.width()
    h = image.height()
    min_x = w
    min_y = h
    max_x = -1
    max_y = -1
    for y in range(h):
        for x in range(w):
            c = image.pixelColor(x, y)
            if c.alpha() == 0:
                continue
            if c.red() == 0 and c.green() == 0 and c.blue() == 0:
                continue
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
    if max_x == -1:
        return QRect(0, 0, 0, 0)
    return QRect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

def make_button_from_overlay(parent, overlay_path, callback):
    full = QPixmap(overlay_path)
    image = full.toImage()
    rect = find_button_rect(image)
    if rect.width() == 0 or rect.height() == 0:
        rect = QRect(0, 0, full.width(), full.height())
    crop = full.copy(rect)
    btn = QPushButton(parent)
    btn.setIcon(QIcon(crop))
    btn.setIconSize(rect.size())
    btn.setGeometry(rect)
    btn.setFlat(True)
    btn.setStyleSheet("border: none; background: transparent;")
    if callback is not None:
        btn.clicked.connect(callback)
    return btn

class ImagePage(QWidget):
    def __init__(self, bg_path, parent=None):
        super().__init__(parent)
        self.bg_label = QLabel(self)
        pix = QPixmap(bg_path)
        if pix.width() == 0 or pix.height() == 0:
            print("PERINGATAN: background tidak ke-load:", bg_path)
            pix = QPixmap(1280, 720)
            pix.fill()
        self.bg_label.setPixmap(pix)
        self.bg_label.setGeometry(0, 0, pix.width(), pix.height())
        self.setFixedSize(pix.width(), pix.height())

class Page1(ImagePage):
    def __init__(self, on_masuk, parent=None):
        super().__init__(BG1, parent)
        self.btn_masuk = make_button_from_overlay(self, BTN_MASUK, on_masuk)

class Page2(ImagePage): #hand tracking connect
    def __init__(self, on_panduan, on_praktik, parent=None):
        super().__init__(BG2, parent)
        self.btn_praktik = make_button_from_overlay(self, BTN2_PRAKTIK, on_praktik)
        self.btn_panduan = make_button_from_overlay(self, BTN2_TUTORIAL, on_panduan)

class Page3(ImagePage):
    def __init__(self, on_abjad, on_angka, on_kosakata, on_kembali_menu, parent=None):
        super().__init__(BG3, parent)
        self.btn_abjad = make_button_from_overlay(self, BTN3_ABJAD, on_abjad)
        self.btn_angka = make_button_from_overlay(self, BTN3_ANGKA, on_angka)
        self.btn_kosakata = make_button_from_overlay(self, BTN3_KOSAKATA, on_kosakata)
        self.btn_menu = make_button_from_overlay(self, BTN3_MENU, on_kembali_menu)

class Page4(ImagePage):
    def __init__(self, on_next, on_kembali_menu, parent=None):
        super().__init__(BG4, parent)
        self.btn_next = make_button_from_overlay(self, BTN4_NEXT, on_next)
        self.btn_menu = make_button_from_overlay(self, BTN4_MENU, on_kembali_menu)

class Page5(ImagePage):
    def __init__(self, on_prev, on_kembali_menu, on_next, parent=None):
        super().__init__(BG5, parent)
        self.btn_prev = make_button_from_overlay(self, BTN5_PREV, on_prev)
        self.btn_menu = make_button_from_overlay(self, BTN5_MENU, on_kembali_menu)
        self.btn_next = make_button_from_overlay(self, BTN5_NEXT, on_next)

class Page6(ImagePage):
    def __init__(self, on_prev, on_kembali_menu, parent=None):
        super().__init__(BG6, parent)
        self.btn_prev = make_button_from_overlay(self, BTN6_PREV, on_prev)
        self.btn_menu = make_button_from_overlay(self, BTN6_MENU, on_kembali_menu)

class Page7(ImagePage):
    def __init__(self, on_kembali_menu, parent=None):
        super().__init__(BG7, parent)
        self.btn_menu = make_button_from_overlay(self, BTN7_MENU, on_kembali_menu)

class Page8(ImagePage):
    def __init__(self, on_kembali_menu, parent=None):
        super().__init__(BG8, parent)
        self.btn_menu = make_button_from_overlay(self, BTN8_MENU, on_kembali_menu)

class MainWindow(QMainWindow):
    def handle_praktik(self): #file hand tracking
        script_path = os.path.join(BASE_DIR, "Project_Pemdas_Isyarat_Track.py")

        try:
            subprocess.Popen([sys.executable, script_path])
            print("Program praktik dibuka.")
        except Exception as e:
            print("Gagal membuka program praktik:", e)
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page1 = Page1(self.go_page2)
        self.page2 = Page2(self.go_page3, self.handle_praktik)
        self.page3 = Page3(self.go_page4, self.go_page7, self.go_page8, self.go_page2)
        self.page4 = Page4(self.go_page5, self.go_page3)
        self.page5 = Page5(self.go_page4, self.go_page3, self.go_page6)
        self.page6 = Page6(self.go_page5, self.go_page3)
        self.page7 = Page7(self.go_page3)
        self.page8 = Page8(self.go_page3)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        self.stack.addWidget(self.page5)
        self.stack.addWidget(self.page6)
        self.stack.addWidget(self.page7)
        self.stack.addWidget(self.page8)

        self.stack.setCurrentWidget(self.page1)

        self.setWindowTitle("Aplikasi Belajar Bahasa Isyarat")
        self.setFixedSize(self.page1.width(), self.page1.height())

    def go_page1(self):
        self.stack.setCurrentWidget(self.page1)

    def go_page2(self):
        self.stack.setCurrentWidget(self.page2)

    def go_page3(self):
        self.stack.setCurrentWidget(self.page3)

    def go_page4(self):
        self.stack.setCurrentWidget(self.page4)

    def go_page5(self):
        self.stack.setCurrentWidget(self.page5)

    def go_page6(self):
        self.stack.setCurrentWidget(self.page6)

    def go_page7(self):
        self.stack.setCurrentWidget(self.page7)

    def go_page8(self):
        self.stack.setCurrentWidget(self.page8)

if __name__ == "__main__":
    print("Folder gambar:", IMG_DIR)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())