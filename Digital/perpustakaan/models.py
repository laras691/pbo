from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Kategori(models.Model):
    id_kategori = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()

    def __str__(self):
        return self.nama

class Buku(models.Model):
    id_buku = models.CharField(max_length=10, unique=True, default='0000')
    judul = models.CharField(max_length=255)
    kode_buku = models.CharField(max_length=20, primary_key=True)
    judul = models.CharField(max_length=200)
    penulis = models.CharField(max_length=100, blank=True, null=True)

    stok = models.PositiveIntegerField(default=0)
   
    def __str__(self):
        return self.judul

    def tampilkan(self):
        return f"{self.judul} - Stok: {self.stok}"

class Pengunjung(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nomor_anggota = models.CharField(max_length=100, unique=True)
    kode_verifikasi = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.nama

    def editProfil(self, nama, email):
        self.nama = nama
        self.email = email
        self.save()

    def gantiPassword(self, passLama, passBaru):
        if check_password(passLama, self.password):
            self.password = make_password(passBaru)
            self.save()
            return True
        return False

class Peminjaman(models.Model):
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('Belum Kembali', 'Belum Kembali'),
        ('Kembali', 'Kembali')
    ])
    tanggal_pinjam = models.DateField()
    tanggal_kembali = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.pengunjung.nama} - {self.buku.judul} ({self.status})"

class Admin(models.Model):
    id_admin = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Laporan(models.Model):
    id_laporan = models.CharField(max_length=20, primary_key=True)
    tanggal_dibuat = models.DateField(null=True, blank=True)
    jenis = models.CharField(max_length=100)
    isi = models.TextField()

    def __str__(self):
        return f"{self.jenis} ({self.tanggal_dibuat})"

class KembalikanBuku(models.Model):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_kembali = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.pengunjung.nama} - {self.buku.judul} (Kembali)"

class GagalPinjam(models.Model):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)
    alasan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pengunjung.nama} gagal pinjam {self.buku.judul}"

class NotifikasiBerhasil(models.Model):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    pesan = models.CharField(max_length=255)
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pengunjung.nama} - {self.pesan}"

class PinjamBuku(models.Model):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(auto_now_add=True)
    tanggal_kembali = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
        ('gagal', 'Gagal'),
    ])

    def __str__(self):
        return f"{self.pengunjung.nama} - {self.buku.judul} ({self.status})"