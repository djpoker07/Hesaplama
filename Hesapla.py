import sys
import math
from datetime import datetime, timedelta
import os
import ctypes

# Windows görev çubuğu simge eşleme düzeltmesi
try:
    myappid = 'sirket.program.tarihhesaplama.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QPushButton,
    QGroupBox, QLabel, QStackedWidget, QCalendarWidget, QDialog, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPalette, QColor, QIcon


def kaynak_yolu(dosya_adi):
    """PyInstaller ile EXE yapıldığında dosyaların doğru okunmasını sağlar"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, dosya_adi)


def my_exception_hook(exctype, value, traceback):
    print("HATA OLUŞTU:", exctype, value, traceback)
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = my_exception_hook


def resmi_tatilleri_ve_arifeleri_olustur(baslangic_yili: int, bitis_yili: int):
    tam_gun_dini_tatiller = set()
    arife_gunleri = set()

    dini_takvim = [
        ("19.03.2026", ["20.03.2026", "21.03.2026", "22.03.2026"]),
        ("26.05.2026", ["27.05.2026", "28.05.2026", "29.05.2026", "30.05.2026"]),
        ("07.03.2027", ["08.03.2027", "09.03.2027", "10.03.2027", "11.03.2027"]),
        ("15.05.2027", ["16.05.2027", "17.05.2027", "18.05.2027", "19.05.2027"]),
        ("25.02.2028", ["26.02.2028", "27.02.2028", "28.02.2028"]),
        ("04.06.2028", ["05.06.2028", "06.06.2028", "07.06.2028", "08.06.2028"]),
        ("13.02.2029", ["14.02.2029", "15.02.2029", "16.02.2029"]),
        ("24.05.2029", ["25.05.2029", "26.05.2029", "27.05.2029", "28.05.2029"]),
        ("03.02.2030", ["04.02.2030", "05.02.2030", "06.02.2030"]),
        ("13.05.2030", ["14.05.2030", "15.05.2030", "16.05.2030", "17.05.2030"]),
        ("23.01.2031", ["24.01.2031", "25.01.2031", "26.01.2031"]),
        ("03.05.2031", ["04.05.2031", "05.05.2031", "06.05.2031", "07.05.2031"]),
        ("12.01.2032", ["13.01.2032", "14.01.2032", "15.01.2032"]),
        ("21.04.2032", ["22.04.2032", "23.04.2032", "24.04.2032", "25.04.2032"]),
        ("31.12.2032", ["01.01.2033", "02.01.2033", "03.01.2033"]),
        ("10.04.2033", ["11.04.2033", "12.04.2033", "13.04.2033", "14.04.2033"]),
        ("20.12.2033", ["21.12.2033", "22.12.2033", "23.12.2033"]),
        ("30.03.2034", ["31.03.2034", "01.04.2034", "02.04.2034", "03.04.2034"]),
        ("09.12.2034", ["10.12.2034", "11.12.2034", "12.12.2034"]),
        ("19.03.2035", ["20.03.2035", "21.03.2035", "22.03.2035", "23.03.2035"]),
    ]

    for arife, bayram_gunleri in dini_takvim:
        arife_gunleri.add(arife)
        for gun in bayram_gunleri:
            tam_gun_dini_tatiller.add(gun)

    for yil in range(baslangic_yili, bitis_yili + 1):
        arife_gunleri.add(f"28.10.{yil}")

    return tam_gun_dini_tatiller, arife_gunleri


DINI_TAM_GUN_TATILLER, ARIFE_GUNLERI = resmi_tatilleri_ve_arifeleri_olustur(2026, 2035)


class TakvimDiyalog(QDialog):
    def __init__(self, ebeveyn=None):
        super().__init__(ebeveyn)
        self.setWindowTitle("Tarih Seç")
        self.setWindowFlags(Qt.Popup)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.takvim = QCalendarWidget()
        self.takvim.setGridVisible(True)
        self.takvim.setFirstDayOfWeek(Qt.Monday)
        self.takvim.activated.connect(self.accept)
        
        layout.addWidget(self.takvim)


class TarihGirisKutusu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.line_edit = QLineEdit()
        self.line_edit.setInputMask("99.99.9999; ") 

        self.btn_takvim = QPushButton("📅")
        self.btn_takvim.setFixedWidth(38)
        self.btn_takvim.setCursor(Qt.PointingHandCursor)
        self.btn_takvim.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                color: #1e293b;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)
        self.btn_takvim.clicked.connect(self.takvim_ac)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_takvim)

    def takvim_ac(self):
        diyalog = TakvimDiyalog(self)
        mevcut_metin = self.line_edit.text().strip()
        if len(mevcut_metin) == 10:
            qdate = QDate.fromString(mevcut_metin, "dd.MM.yyyy")
            if qdate.isValid():
                diyalog.takvim.setSelectedDate(qdate)

        if diyalog.exec() == QDialog.Accepted:
            secilen = diyalog.takvim.selectedDate()
            self.line_edit.setText(secilen.toString("ddMMyyyy"))

    def text(self):
        return self.line_edit.text().strip()

    def setText(self, metin):
        self.line_edit.setText(metin)


class SaatBazliDenetimliHesaplayici(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        form_group = QGroupBox("⚖️ Para Cezası & Saat Detayları")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        self.toplam_saat_input = QLineEdit()
        self.toplam_saat_input.setPlaceholderText("Çalışacağı Saati Giriniz")

        self.baslama_tarihi = TarihGirisKutusu()
        bugun = QDate.currentDate().toString("ddMMyyyy")
        self.baslama_tarihi.setText(bugun)

        self.gunluk_saat_combo = QComboBox()
        self.gunluk_saat_combo.addItems(["2 Saat / Gün", "4 Saat / Gün", "8 Saat / Gün"])
        self.gunluk_saat_combo.setCurrentIndex(1)

        form_layout.addRow("Toplam Ceza / Çalışma Saati:", self.toplam_saat_input)
        form_layout.addRow("İnfaz Başlama Tarihi:", self.baslama_tarihi)
        form_layout.addRow("Günlük Çalışma Süresi:", self.gunluk_saat_combo)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        self.btn_hesapla = QPushButton("⚡ HESAPLA")
        self.btn_hesapla.setCursor(Qt.PointingHandCursor)
        self.btn_hesapla.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; 
                color: white; 
                font-size: 14px;
                font-weight: bold; 
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_hesapla.clicked.connect(self.hesapla)
        main_layout.addWidget(self.btn_hesapla)

        self.sonuc_group = QGroupBox("📊 İnfaz Özeti")
        sonuc_layout = QFormLayout()
        sonuc_layout.setVerticalSpacing(8)

        self.lbl_esdeger_gun = QLabel("0 Gün")
        self.lbl_calisma_gunu = QLabel("0 Gün (Fiili Mesai)")
        self.lbl_calisma_gunu.setStyleSheet("font-weight: bold; color: #1e40af;")
        self.lbl_atlanan_tatil = QLabel("0 Gün")
        self.lbl_bitis_tarihi = QLabel("-")
        self.lbl_bitis_tarihi.setStyleSheet("font-size: 13pt; font-weight: bold; color: #ff3030;")
        self.lbl_yarim_gun_uyari = QLabel("")
        self.lbl_yarim_gun_uyari.setStyleSheet("color: #d97706; font-weight: bold;")
        self.lbl_uyari = QLabel("")
        self.lbl_uyari.setStyleSheet("color: #dc2626; font-weight: bold;")

        sonuc_layout.addRow("Adli Para Cezası Karşılığı:", self.lbl_esdeger_gun)
        sonuc_layout.addRow("Fiilen Çalışılacak Gün:", self.lbl_calisma_gunu)
        sonuc_layout.addRow("Atlanan Tatil / Hafta Sonu:", self.lbl_atlanan_tatil)
        sonuc_layout.addRow("Tahmini Bitiş Tarihi:", self.lbl_bitis_tarihi)
        sonuc_layout.addRow("", self.lbl_yarim_gun_uyari)
        sonuc_layout.addRow("", self.lbl_uyari)

        self.sonuc_group.setLayout(sonuc_layout)
        main_layout.addWidget(self.sonuc_group)
        self.setLayout(main_layout)

    def sifirla(self):
        self.toplam_saat_input.clear()
        bugun = QDate.currentDate().toString("ddMMyyyy")
        self.baslama_tarihi.setText(bugun)
        self.gunluk_saat_combo.setCurrentIndex(1)
        self.lbl_esdeger_gun.setText("0 Gün")
        self.lbl_calisma_gunu.setText("0 Gün (Fiili Mesai)")
        self.lbl_atlanan_tatil.setText("0 Gün")
        self.lbl_bitis_tarihi.setText("-")
        self.lbl_yarim_gun_uyari.setText("")
        self.lbl_uyari.setText("")

    def hesapla(self):
        try:
            toplam_saat = float(self.toplam_saat_input.text().strip())
            if toplam_saat <= 0:
                raise ValueError
        except ValueError:
            self.lbl_uyari.setText("Lütfen geçerli bir saat miktarı girin!")
            return

        str_baslangic = self.baslama_tarihi.text()
        if len(str_baslangic) < 10:
            self.lbl_uyari.setText("Lütfen geçerli bir başlama tarihi girin!")
            return

        try:
            mevcut_tarih = datetime.strptime(str_baslangic, "%d.%m.%Y").date()
        except ValueError:
            self.lbl_uyari.setText("Geçersiz tarih formatı!")
            return

        self.lbl_uyari.setText("")
        self.lbl_yarim_gun_uyari.setText("")

        if toplam_saat > 2190:
            toplam_saat = 2190.0

        gunluk_saat_map = {0: 2, 1: 4, 2: 8}
        gunluk_saat = gunluk_saat_map[self.gunluk_saat_combo.currentIndex()]
        SABIT_TAM_GUN_TATILLER = {"01.01", "23.04", "01.05", "19.05", "15.07", "30.08", "29.10"}

        kalan_dakika = int(round(toplam_saat * 60))
        gunluk_dakika = int(round(gunluk_saat * 60))

        atlanan_tatil_sayisi = 0
        fiili_is_gunu_sayisi = 0.0  
        son_gun_calisma_saati = 0

        while kalan_dakika > 0:
            tarih_str = mevcut_tarih.strftime("%d.%m.%Y")
            gun_ay_str = mevcut_tarih.strftime("%d.%m")

            is_hafta_sonu = mevcut_tarih.weekday() >= 5
            is_sabit_tatil = gun_ay_str in SABIT_TAM_GUN_TATILLER
            is_dini_bayram = tarih_str in DINI_TAM_GUN_TATILLER
            is_arife = tarih_str in ARIFE_GUNLERI

            if is_hafta_sonu or is_sabit_tatil or is_dini_bayram:
                atlanan_tatil_sayisi += 1
            else:
                maks_gunluk_dakika = gunluk_dakika // 2 if is_arife else gunluk_dakika
                calisilacak_dakika = min(maks_gunluk_dakika, kalan_dakika)
                son_gun_calisma_saati = calisilacak_dakika / 60.0
                kalan_dakika -= calisilacak_dakika
                fiili_is_gunu_sayisi += (calisilacak_dakika / gunluk_dakika)

            if kalan_dakika <= 0:
                break
            mevcut_tarih += timedelta(days=1)

        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        bitis_gun_adi = gunler[mevcut_tarih.weekday()]
        esdeger_ceza_gunu = toplam_saat / 2

        if esdeger_ceza_gunu.is_integer():
            self.lbl_esdeger_gun.setText(f"{int(esdeger_ceza_gunu)} Gün Cezaya Denk")
        else:
            self.lbl_esdeger_gun.setText(f"{esdeger_ceza_gunu:.1f} Gün Cezaya Denk")

        self.lbl_calisma_gunu.setText(f"{int(round(fiili_is_gunu_sayisi))} Gün (Fiili Mesai)")
        self.lbl_atlanan_tatil.setText(f"{atlanan_tatil_sayisi} Gün")
        self.lbl_bitis_tarihi.setText(f"{mevcut_tarih.strftime('%d.%m.%Y')} ({bitis_gun_adi})")

class KamuHesaplamaPenceresi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        group_box = QGroupBox("📅 Tarih Bilgileri")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        layout_tarih1 = QHBoxLayout()
        lbl_tarih1 = QLabel("Başlama Tarihi:")
        lbl_tarih1.setFixedWidth(150)
        self.date_input1 = TarihGirisKutusu()
        layout_tarih1.addWidget(lbl_tarih1)
        layout_tarih1.addWidget(self.date_input1)
        group_layout.addLayout(layout_tarih1)

        layout_tarih2 = QHBoxLayout()
        lbl_tarih2 = QLabel("Koşullu Salıverme:")
        lbl_tarih2.setFixedWidth(150)
        self.date_input2 = TarihGirisKutusu()
        layout_tarih2.addWidget(lbl_tarih2)
        layout_tarih2.addWidget(self.date_input2)
        group_layout.addLayout(layout_tarih2)

        layout_tarih3 = QHBoxLayout()
        lbl_tarih3 = QLabel("Kamu Hiz. Başlama:")
        lbl_tarih3.setFixedWidth(150)
        self.date_input3 = TarihGirisKutusu()
        layout_tarih3.addWidget(lbl_tarih3)
        layout_tarih3.addWidget(self.date_input3)
        group_layout.addLayout(layout_tarih3)

        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        bugun = QDate.currentDate().toString("ddMMyyyy")
        self.date_input1.setText(bugun)
        self.date_input2.setText(bugun)
        self.date_input3.setText(bugun)

        btn_hesapla = QPushButton("⚡ HESAPLA")
        btn_hesapla.setCursor(Qt.PointingHandCursor)
        btn_hesapla.setStyleSheet("""
            QPushButton {
                padding: 10px; font-size: 14px; font-weight: bold; 
                background-color: #2563eb; color: white; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        btn_hesapla.clicked.connect(self.tarihleri_hesapla)
        main_layout.addWidget(btn_hesapla)

        self.sonuc_box = QGroupBox("📋 İnfaz Özeti")
        sonuc_layout = QVBoxLayout()
        self.lbl_sonuc = QLabel("")
        self.lbl_sonuc.setStyleSheet("font-size: 13px; color: #1e293b;")
        sonuc_layout.addWidget(self.lbl_sonuc)
        self.sonuc_box.setLayout(sonuc_layout)

        main_layout.addWidget(self.sonuc_box)
        self.setLayout(main_layout)

    def sifirla(self):
        bugun = QDate.currentDate().toString("ddMMyyyy")
        self.date_input1.setText(bugun)
        self.date_input2.setText(bugun)
        self.date_input3.setText(bugun)
        self.lbl_sonuc.setText("")

    def tarihleri_hesapla(self):
        str_tarih1 = self.date_input1.text()
        str_tarih2 = self.date_input2.text()
        str_tarih3 = self.date_input3.text()

        if len(str_tarih1) < 10 or len(str_tarih2) < 10 or len(str_tarih3) < 10:
            return

        tarih1 = datetime.strptime(str_tarih1, "%d.%m.%Y").date()
        tarih2 = datetime.strptime(str_tarih2, "%d.%m.%Y").date()
        tarih3 = datetime.strptime(str_tarih3, "%d.%m.%Y").date()

        toplam_gun = (tarih2 - tarih1).days
        kamu_gun_ham = toplam_gun / 3.0
        kamu_gun_yuv = math.ceil(kamu_gun_ham)
        kamu_bitis_tarihi = tarih3 + timedelta(days=kamu_gun_yuv)

        sonuc_metni = (
            f"<b>Başlama Tarihi:</b> {str_tarih1}<br>"
            f"<b>Koşullu Salıverme:</b> {str_tarih2}<br>"
            f"<b>Toplam Süre:</b> {toplam_gun} Gün<br>"
            f"<b>Kamu Hizmeti Süresi (1/3):</b> {kamu_gun_yuv} Gün<br>"
            # BURADA font-size: 13pt; eklenerek yazı büyütüldü:
            f"<b>Kamu Hiz. Bitiş Tarihi:</b> <b style='color: #ff3030; font-size: 13pt;'>{kamu_bitis_tarihi.strftime('%d.%m.%Y')}</b>"
        )
        self.lbl_sonuc.setText(sonuc_metni)


class AnaBirlesikPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adli Para Cezası ve Kamu Hizmeti Hesaplama")
        self.setMinimumSize(580, 560)

        icon_path = kaynak_yolu("icon.ico")
        if os.path.exists(icon_path):
            appIcon = QIcon(icon_path)
            self.setWindowIcon(appIcon)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        btn_layout = QHBoxLayout()
        self.btn_modul1 = QPushButton("⚖️ Adli Para Cezası Hesaplama")
        self.btn_modul2 = QPushButton("📅 Kamu Hizmeti Hesaplama")

        for btn in (self.btn_modul1, self.btn_modul2):
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(42)

        self.btn_modul1.clicked.connect(lambda: self.sayfa_degistir(0))
        self.btn_modul2.clicked.connect(lambda: self.sayfa_degistir(1))

        self.btn_genel_sifirla = QPushButton("🔄 Sıfırla")
        self.btn_genel_sifirla.setFixedWidth(90)
        self.btn_genel_sifirla.clicked.connect(self.hepsini_sifirla)

        btn_layout.addWidget(self.btn_modul1, stretch=2)
        btn_layout.addWidget(self.btn_modul2, stretch=2)
        btn_layout.addWidget(self.btn_genel_sifirla, stretch=0)
        main_layout.addLayout(btn_layout)

        self.stack = QStackedWidget()
        self.modul1 = SaatBazliDenetimliHesaplayici()
        self.modul2 = KamuHesaplamaPenceresi()
        self.stack.addWidget(self.modul1)
        self.stack.addWidget(self.modul2)

        main_layout.addWidget(self.stack)
        self.setCentralWidget(central_widget)
        self.sayfa_degistir(0)

    def hepsini_sifirla(self):
        self.modul1.sifirla()
        self.modul2.sifirla()

    def sayfa_degistir(self, index):
        self.stack.setCurrentIndex(index)
        aktif = "background-color: #2563eb; color: #ffffff; font-weight: bold; border-radius: 8px;"
        pasif = "background-color: #ffffff; color: #475569; font-weight: bold; border-radius: 8px; border: 1px solid #cbd5e1;"
        
        if index == 0:
            self.btn_modul1.setStyleSheet(aktif)
            self.btn_modul2.setStyleSheet(pasif)
        else:
            self.btn_modul1.setStyleSheet(pasif)
            self.btn_modul2.setStyleSheet(aktif)


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # --- TEMAYI SABİTLEME KODLARI ---
    app.setStyle("Fusion")  # Windows stili yerine platform bağımsız Fusion stilini zorlar
    
    # Sabit bir açık tema paleti oluşturarak sistemin koyu/açık mod geçişlerini engeller
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(30, 41, 59))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 247, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(30, 41, 59))
    palette.setColor(QPalette.Text, QColor(30, 41, 59))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(30, 41, 59))
    palette.setColor(QPalette.Highlight, QColor(37, 99, 235))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    # ---------------------------------

    icon_path = kaynak_yolu("icon.ico")
    if os.path.exists(icon_path):
        appIcon = QIcon(icon_path)
        app.setWindowIcon(appIcon)

    window = AnaBirlesikPencere()
    window.show()

    sys.exit(app.exec())