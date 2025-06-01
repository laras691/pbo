from django.contrib import admin
from .models import Buku
from .models import (
    Pengunjung, Admin, PinjamBuku, KembalikanBuku,
    GagalPinjam, NotifikasiBerhasil,
    Kategori, Peminjaman, Laporan
)

admin.site.register(Buku)
admin.site.register(Pengunjung)
admin.site.register(Admin)
admin.site.register(PinjamBuku)
admin.site.register(KembalikanBuku)
admin.site.register(GagalPinjam)
admin.site.register(NotifikasiBerhasil)
admin.site.register(Kategori)
admin.site.register(Peminjaman)
admin.site.register(Laporan)