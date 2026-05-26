import streamlit as st
import math
from datetime import datetime

# ========== STRUKTUR DATA: DOUBLY LINKED LIST ==========
class KendaraanNode:
    def __init__(self, plat, merk, pemilik, status):
        self.plat = plat.upper()
        self.merk = merk
        self.pemilik = pemilik
        self.status = status.upper()  # VIP atau REGULER
        self.waktu_masuk = datetime.now()
        self.prev = None
        self.next = None

class SistemParkirValet:
    def __init__(self):
        self.head = None  # Pintu Keluar (Paling Depan)
        self.tail = None  # Ujung Lajur (Paling Belakang)
        self.kapasitas = 0
        self.total_slot_maksimal = 10  # Batas kapasitas parkir default

    def parkir_vip(self, plat, merk, pemilik):
        if self.kapasitas >= self.total_slot_maksimal:
            return False, "Kapasitas parkir sudah penuh!"
            
        mobil_baru = KendaraanNode(plat, merk, pemilik, "VIP")
        if self.head is None:
            self.head = mobil_baru
            self.tail = mobil_baru
        else:
            mobil_baru.next = self.head
            self.head.prev = mobil_baru
            self.head = mobil_baru
        self.kapasitas += 1
        return True, f"Kendaraan VIP {merk} ({mobil_baru.plat}) masuk di antrean DEPAN (HEAD)."

    def parkir_reguler(self, plat, merk, pemilik):
        if self.kapasitas >= self.total_slot_maksimal:
            return False, "Kapasitas parkir sudah penuh!"

        mobil_baru = KendaraanNode(plat, merk, pemilik, "REGULER")
        if self.tail is None:
            self.head = mobil_baru
            self.tail = mobil_baru
        else:
            mobil_baru.prev = self.tail
            self.tail.next = mobil_baru
            self.tail = mobil_baru
        self.kapasitas += 1
        return True, f"Kendaraan Reguler {merk} ({mobil_baru.plat}) masuk di antrean BELAKANG (TAIL)."

    def proses_keluar(self, target_plat):
        target_plat = target_plat.upper()
        current = self.head
        
        while current:
            if current.plat == target_plat:
                waktu_keluar = datetime.now()
                selisih_waktu = waktu_keluar - current.waktu_masuk
                
                # Simulasi: 1 menit nyata = 1 jam parkir
                lama_jam = math.ceil(selisih_waktu.total_seconds() / 60)
                if lama_jam == 0: lama_jam = 1 
                
                if current.status == "VIP":
                    biaya = 20000 + ((lama_jam - 1) * 10000)
                else:
                    biaya = 5000 + ((lama_jam - 1) * 3000)

                data_struk = {
                    "plat": current.plat,
                    "merk": current.merk,
                    "pemilik": current.pemilik,
                    "status": current.status,
                    "waktu_masuk": current.waktu_masuk.strftime("%H:%M:%S"),
                    "waktu_keluar": waktu_keluar.strftime("%H:%M:%S"),
                    "lama_jam": lama_jam,
                    "total_biaya": biaya
                }

                # Hapus Node
                if current == self.head:
                    self.head = self.head.next
                    if self.head: self.head.prev = None
                    else: self.tail = None 
                elif current == self.tail:
                    self.tail = self.tail.prev
                    if self.tail: self.tail.next = None
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev
                
                self.kapasitas -= 1
                return data_struk
                
            current = current.next
        return None

    def cari_kendaraan(self, target_plat):
        target_plat = target_plat.upper()
        current = self.head
        posisi = 1
        
        while current:
            if current.plat == target_plat:
                return {
                    "posisi": positioning,
                    "plat": current.plat,
                    "merk": current.merk,
                    "pemilik": current.pemilik,
                    "status": current.status,
                    "jam_masuk": current.waktu_masuk.strftime("%H:%M:%S"),
                    "mobil_depan": current.prev.plat if current.prev else "Tidak ada (Sudah paling depan)",
                    "mobil_belakang": current.next.plat if current.next else "Tidak ada (Sudah paling belakang)"
                }
            current = current.next
            posisi += 1
        return None

    def konversi_ke_matriks(self):
        data = []
        current = self.head
        nomor = 1
        while current:
            jam = current.waktu_masuk.strftime("%H:%M:%S")
            data.append([nomor, current.plat, current.merk, current.pemilik, current.status, jam])
            current = current.next
            nomor += 1
        return data

    def reset_parkiran(self):
        self.head = None
        self.tail = None
        self.kapasitas = 0


# ========== APLIKASI UTAMA (STREAMLIT UI) ==========

st.set_page_config(page_title="Smart Parking System Pro", page_icon="🏢", layout="centered")

# Inisialisasi session state konfirmasi di bagian paling atas
if 'konfirmasi_reset' not in st.session_state:
    st.session_state.konfirmasi_reset = False

# --- KUSTOMISASI GRADASI BACKGROUND GLOBAL ---
# Jika masuk zona bahaya reset, warna berubah jadi gradasi merah-pink pastel yang soft
if st.session_state.konfirmasi_reset:
    bg_gradient = "linear-gradient(to bottom right, #ffcccc, #fff5f5)"
else:
    # Gradasi utama sesuai request dari "#999966" ke "#ccffcc"
    bg_gradient = "linear-gradient(to bottom right, #999966, #ccffcc)"

st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            background-attachment: fixed;
            transition: background 0.5s ease-in-out;
        }}
        
        /* Tambahan sedikit tweak agar tab menu terlihat lebih kontras dan menyatu dengan gradasi */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(255, 255, 255, 0.5);
            padding: 5px;
            border-radius: 8px;
        }}
    </style>
""", unsafe_allow_html=True)


st.title("🚗 Smart Parking System")
st.caption("Sistem Manajemen Parkir Terintegrasi - Berbasis Doubly Linked List")

# Inisialisasi Session State data
if 'parkiran' not in st.session_state:
    st.session_state.parkiran = SistemParkirValet()
if 'riwayat_pendapatan' not in st.session_state:
    st.session_state.riwayat_pendapatan = []

parkiran = st.session_state.parkiran

# MEMBUAT 6 TAB MENU
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📥 Check-In", 
    "📤 Check-Out", 
    "📊 Denah Parkir", 
    "🔍 Cari Mobil", 
    "💰 Keuangan", 
    "⚙️ Pengaturan"
])

# --- MENU 1: CHECK-IN ---
with tab1:
    st.header("Form Registrasi Kendaraan Masuk")
    sisa_slot = parkiran.total_slot_maksimal - parkiran.kapasitas
    st.info(f"Slot Tersedia: **{sisa_slot}** / {parkiran.total_slot_maksimal} Unit")
    
    with st.form("form_pendaftaran", clear_on_submit=True):
        plat_input = st.text_input("Plat Nomor Kendaraan", placeholder="Contoh: B 1234 ABC")
        merk_input = st.text_input("Merk Kendaraan", placeholder="Contoh: Honda Brio Hitam")
        pemilik_input = st.text_input("Nama Lengkap Pemilik", placeholder="Contoh: Ahmad Subarjo")
        status_input = st.radio("Pilih Tipe Layanan Parkir", ["Reguler", "VIP"])
        
        proses_masuk = st.form_submit_button("Daftarkan & Parkirkan")
        
        if proses_masuk:
            if plat_input and merk_input and pemilik_input:
                if "VIP" in status_input:
                    sukses, hasil_pesan = parkiran.parkir_vip(plat_input, merk_input, pemilik_input)
                else:
                    sukses, hasil_pesan = parkiran.parkir_reguler(plat_input, merk_input, pemilik_input)
                
                if sukses:
                    st.success(hasil_pesan)
                else:
                    st.error(hasil_pesan)
            else:
                st.error("Gagal! Semua kolom formulir data kendaraan wajib diisi.")

# --- MENU 2: CHECK-OUT ---
with tab2:
    st.header("Form Billing Kasir")
    plat_keluar = st.text_input("Masukkan Plat Nomor Mobil yang Ingin Keluar", key="input_checkout")
    tombol_keluar = st.button("Proses Pembayaran Keluar", type="primary")
    
    if tombol_keluar:
        if plat_keluar:
            struk = parkiran.proses_keluar(plat_keluar)
            if struk:
                st.success("Akses Terverifikasi! Kendaraan dilepaskan dari lajur antrean.")
                st.session_state.riwayat_pendapatan.append(struk)
                
                st.markdown("### 🧾 STRUK SMART PARKING")
                st.markdown("---")
                col_kiri, col_kanan = st.columns(2)
                with col_kiri:
                    st.markdown(f"**Plat Nomor** :
