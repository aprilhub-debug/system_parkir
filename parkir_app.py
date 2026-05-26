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
                    "posisi": posisi,
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

# Inisialisasi session state konfirmasi di bagian paling atas agar warna background sinkron
if 'konfirmasi_reset' not in st.session_state:
    st.session_state.konfirmasi_reset = False

# --- KUSTOMISASI BACKGROUND WARNA GLOBAL (SEJAK AWAL MASUK) ---
# Jika dalam mode konfirmasi reset, warna background menjadi merah pastel lembut.
# Jika kondisi normal, berwarna mint-blue grey modern yang bersih (#f4f6f9).
if st.session_state.konfirmasi_reset:
    bg_color = "#fff5f5"
else:
    bg_color = "#f4f6f9"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            transition: background-color 0.4s ease-in-out;
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
                    st.markdown(f"**Plat Nomor** : {struk['plat']}")
                    st.markdown(f"**Kendaraan** : {struk['merk']}")
                    st.markdown(f"**Pemilik** : {struk['pemilik']}")
                    st.markdown(f"**Status Kelas** : {struk['status']}")
                with col_kanan:
                    st.markdown(f"**Jam Masuk** : {struk['waktu_masuk']}")
                    st.markdown(f"**Jam Keluar** : {struk['waktu_keluar']}")
                    st.markdown(f"**Durasi Parkir** : {struk['lama_jam']} Jam (Skala Simulasi)")
                st.markdown("---")
                st.info(f"### TOTAL TAGIHAN: Rp {struk['total_biaya']:,}")
            else:
                st.error(f"[-] ERROR: Kendaraan dengan plat nomor '{plat_keluar.upper()}' tidak ditemukan.")
        else:
            st.warning("Silakan isi plat nomor target terlebih dahulu.")

# --- MENU 3: DENAH PARKIR ---
with tab3:
    st.header("Monitoring Denah Jalur Parkir")
    st.metric(label="Jumlah Kendaraan Terparkir Saat Ini", value=f"{parkiran.kapasitas} Unit")
    
    list_mobil = parkiran.konversi_ke_matriks()
    if list_mobil:
        st.markdown("**Urutan Lajur Parkir**")
        nama_kolom = ["No", "Plat Nomor", "Merk Kendaraan", "Nama Pemilik", "Status", "Jam Masuk"]
        tabel_statis = [dict(zip(nama_kolom, mobil)) for mobil in list_mobil]
        st.table(tabel_statis)
    else:
        st.info("Kondisi Parkiran Kosong. Belum ada kendaraan yang terdaftar masuk.")

# --- MENU 4: CARI MOBIL ---
with tab4:
    st.header("🔍 Pelacakan Posisi Kendaraan")
    st.caption("Gunakan menu ini untuk mengetahui di urutan ke berapa mobil berada di dalam antrean.")
    plat_cari = st.text_input("Masukkan Plat Nomor yang Dicari")
    
    if st.button("Lacak Posisi"):
        if plat_cari:
            hasil_cari = parkiran.cari_kendaraan(plat_cari)
            if hasil_cari:
                st.success(f"Kendaraan ditemukan pada urutan ke-**{hasil_cari['posisi']}** dari pintu keluar!")
                st.markdown("### 📋 Detail Posisi Antrean")
                st.write(f"**Nama Pemilik:** {hasil_cari['pemilik']} ({hasil_cari['status']})")
                st.write(f"**Model Mobil:** {hasil_cari['merk']}")
                st.write(f"**Jam Masuk:** {hasil_cari['jam_masuk']}")
                st.markdown("---")
                st.warning(f"⬅️ **Mobil di Depannya:** {hasil_cari['mobil_depan']}")
                st.info(f"➡️ **Mobil di Belakangnya:** {hasil_cari['mobil_belakang']}")
            else:
                st.error("Kendaraan tidak ditemukan di dalam area parkir.")
        else:
            st.warning("Masukkan plat nomor terlebih dahulu.")

# --- MENU 5: KEUANGAN ---
with tab5:
    st.header("💰 Laporan Pendapatan Kasir")
    st.caption("Data pendapatan kumulatif dari kendaraan yang sudah melakukan Check-Out.")
    
    riwayat = st.session_state.riwayat_pendapatan
    if riwayat:
        total_omset = sum(item['total_biaya'] for item in riwayat)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Pendapatan", f"Rp {total_omset:,}")
        col_m2.metric("Total Mobil Keluar", f"{len(riwayat)} Unit")
        
        st.markdown("### 📜 Riwayat Transaksi")
        kolom_keuangan = ["Plat Nomor", "Status Kelas", "Durasi", "Total Bayar"]
        matriks_keuangan = []
        for r in riwayat:
            matriks_keuangan.append([r['plat'], r['status'], f"{r['lama_jam']} Jam", f"Rp {r['total_biaya']:,}"])
            
        tabel_keuangan = [dict(zip(kolom_keuangan, baris)) for baris in matriks_keuangan]
        st.table(tabel_keuangan)
    else:
        st.info("Belum ada transaksi keuangan tercatat. Silakan lakukan proses Check-Out terlebih dahulu.")

# --- MENU 6: PENGATURAN SYSTEM ---
with tab6:
    st.header("⚙️ Pengontrol Sistem Parkir")
    st.caption("Menu utilitas untuk memodifikasi parameter sistem atau meriset data memori.")
    
    # Fitur Ubah Kapasitas Dinamis
    kapasitas_baru = st.number_input("Atur Ulang Batas Maksimal Slot Parkir", min_value=1, max_value=50, value=parkiran.total_slot_maksimal)
    if st.button("Simpan Batas Kapasitas"):
        parkiran.total_slot_maksimal = kapasitas_baru
        st.success(f"Kapasitas maksimal berhasil diubah menjadi {kapasitas_baru} unit!")
        
    st.markdown("---")
    st.subheader("⚠️ Zona Bahaya")
    st.write("Aksi di bawah ini akan menghapus seluruh data antrean kendaraan di dalam memori saat ini.")

    # Tombol pemicu awal reset
    if st.button("RESET & KOSONGKAN SELURUH PARKIRAN", type="primary", use_container_width=True):
        st.session_state.konfirmasi_reset = True
        st.rerun()

    # Tampilan Pop-up Konfirmasi jika status konfirmasi_reset bernilai True
    if st.session_state.konfirmasi_reset:
        st.markdown("""
            <div style="background-color: #ffffff; padding: 25px; border-top: 6px solid #ff4b4b; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-top: 15px; margin-bottom: 20px;">
                <h4 style="color: #ff4b4b; margin-top: 0; margin-bottom: 10px;">🛑 Konfirmasi Pengosongan Lapangan Parkir</h4>
                <p style="color: #31333F; font-size: 14.5px; line-height: 1.6; margin-bottom: 0;">
                    Tindakan ini bersifat <b>permanen</b>. Seluruh data kendaraan terparkir saat ini beserta seluruh data laporan keuangan kasir akan <b>dihapus total</b> dari memori sistem. Apakah Anda yakin?
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_ya, col_batal = st.columns(2)
        
        with col_ya:
            if st.button("Ya, Kosongkan Sekarang", type="primary", use_container_width=True):
                parkiran.reset_parkiran()
                st.session_state.riwayat_pendapatan = []
                st.session_state.konfirmasi_reset = False
                st.success("Sistem berhasil dikosongkan total!")
                st.rerun()
                
        with col_batal:
            if st.button("Batalkan Proses", type="secondary", use_container_width=True):
                st.session_state.konfirmasi_reset = False
                st.rerun()
