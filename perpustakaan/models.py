from django.db import models

class Kategori(models.Model):
    id_kategori = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()

    def str(self):
        return self.nama

class Buku(models.Model):
    id_buku = models.CharField(max_length=20, primary_key=True)
    judul = models.CharField(max_length=200)
    stok = models.PositiveIntegerField(default=0)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def tampilkan(self):
        return f"{self.judul} - Stok: {self.stok}"

class PinjamBuku(Buku):
    def tampilkan(self):
        return f"Pinjam: {self.judul}"

class KembalikanBuku(Buku):
    def tampilkan(self):
        return f"Kembalikan: {self.judul}"

class GagalPinjam(Buku):
    def tampilkanError(self):
        return f"Gagal: {self.judul} tidak tersedia"
    
    def tampilkan(self):
        return self.tampilkanError()

class NotifikasiBerhasil(Buku):
    def tampilkanSukses(self):
        return f"Berhasil memproses: {self.judul}"
    
    def tampilkan(self):
        return self.tampilkanSukses()

class Pengunjung(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nomor_anggota = models.CharField(max_length=100, unique=True)
    kode_verifikasi = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def str(self):
        return self.nama

class Peminjaman(models.Model):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    buku = models.ForeignKey(PinjamBuku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(auto_now_add=True)
    tanggal_kembali = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
        ('gagal', 'Gagal'),
    ])

    def str(self):
        return f"{self.pengunjung.nama} - {self.buku.judul} ({self.status})"

class Admin(models.Model):
    id_admin = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)

    def str(self):
        return self.nama

class Laporan(models.Model):
    id_laporan = models.CharField(max_length=20, primary_key=True)
    tanggal_dibuat = models.DateField(auto_now_add=True)
    jenis = models.CharField(max_length=100)
    isi = models.TextField()

    def str(self):
        return f"{self.jenis} ({self.tanggal_dibuat})"