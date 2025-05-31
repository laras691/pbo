from django.db import models
from django.contrib.auth.models import User

class Buku(models.Model):
    judul = models.CharField(max_length=100)
    # ... atribut lainnya

class Peminjaman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(auto_now_add=True)
