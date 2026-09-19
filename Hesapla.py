from datetime import datetime, timedelta
import math
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Adli Para Cezası ve Kamu Hizmeti Hesaplama",
    page_icon="⚖️",
    layout="centered",
)


# Şifre Kontrol Fonksiyonu
def check_password():
  SIFRE = "0707"

  def password_entered():
    if st.session_state["password"] == SIFRE:
      st.session_state["password_correct"] = True
      del st.session_state["password"]
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    st.text_input(
        "🔒 Lütfen Erişim Şifresini Girin:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    return False
  elif not st.session_state["password_correct"]:
    st.text_input(
        "🔒 Lütfen Erişim Şifresini Girin:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    st.error("😕 Şifre yanlış")
    return False
  else:
    return True


# Şifre doğru değilse durdur
if not check_password():
  st.stop()


# Tatil Günlerini Oluşturan Fonksiyon
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


DINI_TAM_GUN_TATILLER, ARIFE_GUNLERI = resmi_tatilleri_ve_arifeleri_olustur(
    2026, 2035
)

# Arayüz Başlığı
st.markdown(
    "<h2 style='text-align: center;'>⚖️ İnfaz ve Süre Hesaplama Aracı</h2>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Sekmeler (Modüller Arası Geçiş)
tab1, tab2 = st.tabs(
    ["⚖️ Adli Para Cezası Hesaplama", "📅 Kamu Hizmeti Hesaplama"]
)

bugun_str = datetime.today().strftime("%d.%m.%Y")

# --- MODÜL 1: Adli Para Cezası ---
with tab1:
  st.subheader("Para Cezası & Saat Detayları")
  toplam_saat_input = st.text_input(
      "Toplam Ceza / Çalışma Saati:", placeholder="Örn: 40"
  )
  baslama_tarihi_str = st.text_input(
      "İnfaz Başlama Tarihi (GG.AA.YYYY):", value=bugun_str
  )
  gunluk_saat_combo = st.selectbox(
      "Günlük Çalışma Süresi:", ["2 Saat / Gün", "4 Saat / Gün", "8 Saat / Gün"], index=1
  )

  if st.button("⚡ HESAPLA (Adli Para)", use_container_width=True):
    try:
      toplam_saat = float(toplam_saat_input.strip())
      if toplam_saat <= 0:
        raise ValueError
    except ValueError:
      st.error("Lütfen geçerli bir saat miktarı girin!")
      st.stop()

    try:
      baslama_tarihi = datetime.strptime(
          baslama_tarihi_str.strip(), "%d.%m.%Y"
      ).date()
    except ValueError:
      st.error("Lütfen tarihi GG.AA.YYYY formatında girin (Örn: 19.09.2026)")
      st.stop()

    if toplam_saat > 2190:
      toplam_saat = 2190.0

    gunluk_saat_map = {"2 Saat / Gün": 2, "4 Saat / Gün": 4, "8 Saat / Gün": 8}
    gunluk_saat = gunluk_saat_map[gunluk_saat_combo]
    SABIT_TAM_GUN_TATILLER = {
        "01.01",
        "23.04",
        "01.05",
        "19.05",
        "15.07",
        "30.08",
        "29.10",
    }

    kalan_dakika = int(round(toplam_saat * 60))
    gunluk_dakika = int(round(gunluk_saat * 60))

    atlanan_tatil_sayisi = 0
    fiili_is_gunu_sayisi = 0.0
    mevcut_tarih = baslama_tarihi

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
        kalan_dakika -= calisilacak_dakika
        fiili_is_gunu_sayisi += calisilacak_dakika / gunluk_dakika

      if kalan_dakika <= 0:
        break
      mevcut_tarih += timedelta(days=1)

    gunler = [
        "Pazartesi",
        "Salı",
        "Çarşamba",
        "Perşembe",
        "Cuma",
        "Cumartesi",
        "Pazar",
    ]
    bitis_gun_adi = gunler[mevcut_tarih.weekday()]
    esdeger_ceza_gunu = toplam_saat / 2

    st.markdown("---")
    st.markdown("### 📊 İnfaz Özeti")
    if esdeger_ceza_gunu.is_integer():
      st.info(f"**Adli Para Cezası Karşılığı:** {int(esdeger_ceza_gunu)} Gün Cezaya Denk")
    else:
      st.info(f"**Adli Para Cezası Karşılığı:** {esdeger_ceza_gunu:.1f} Gün Cezaya Denk")

    st.success(f"**Fiilen Çalışılacak Gün:** {int(round(fiili_is_gunu_sayisi))} Gün (Fiili Mesai)")
    st.write(f"**Atlanan Tatil / Hafta Sonu:** {atlanan_tatil_sayisi} Gün")
    st.markdown(
        f"**Tahmini Bitiş Tarihi:** <span"
        f" style='color: #ff3030; font-size: 14pt; font-weight: bold;'>{mevcut_tarih.strftime('%d.%m.%Y')}"
        f" ({bitis_gun_adi})</span>",
        unsafe_allow_html=True,
    )


# --- MODÜL 2: Kamu Hizmeti Hesaplama ---
with tab2:
  st.subheader("📅 Tarih Bilgileri")
  date_input1_str = st.text_input(
      "Başlama Tarihi (GG.AA.YYYY):", value=bugun_str, key="d1"
  )
  date_input2_str = st.text_input(
      "Koşullu Salıverme Tarihi (GG.AA.YYYY):", value=bugun_str, key="d2"
  )
  date_input3_str = st.text_input(
      "Kamu Hiz. Başlama Tarihi (GG.AA.YYYY):", value=bugun_str, key="d3"
  )

  if st.button("⚡ HESAPLA (Kamu Hizmeti)", use_container_width=True):
    try:
      tarih1 = datetime.strptime(date_input1_str.strip(), "%d.%m.%Y").date()
      tarih2 = datetime.strptime(date_input2_str.strip(), "%d.%m.%Y").date()
      tarih3 = datetime.strptime(date_input3_str.strip(), "%d.%m.%Y").date()
    except ValueError:
      st.error(
          "Lütfen tüm tarihleri GG.AA.YYYY formatında doğru girin (Örn:"
          " 19.09.2026)"
      )
      st.stop()

    toplam_gun = (tarih2 - tarih1).days
    if toplam_gun < 0:
      st.error("Koşullu salıverme tarihi, başlama tarihinden önce olamaz!")
    else:
      kamu_gun_ham = toplam_gun / 3.0
      kamu_gun_yuv = math.ceil(kamu_gun_ham)
      kamu_bitis_tarihi = tarih3 + timedelta(days=kamu_gun_yuv)

      st.markdown("---")
      st.markdown("### 📋 İnfaz Özeti")
      st.write(f"**Başlama Tarihi:** {tarih1.strftime('%d.%m.%Y')}")
      st.write(f"**Koşullu Salıverme:** {tarih2.strftime('%d.%m.%Y')}")
      st.write(f"**Toplam Süre:** {toplam_gun} Gün")
      st.write(f"**Kamu Hizmeti Süresi (1/3):** {kamu_gun_yuv} Gün")
      st.markdown(
          f"**Kamu Hiz. Bitiş Tarihi:** <span style='color: #ff3030; font-size:"
          f" 14pt; font-weight:"
          f" bold;'>{kamu_bitis_tarihi.strftime('%d.%m.%Y')}</span>",
          unsafe_allow_html=True,
      )
