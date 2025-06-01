from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import (
    Pengunjung, Admin, PinjamBuku, KembalikanBuku,
    GagalPinjam, NotifikasiBerhasil,
    Kategori, Peminjaman, Laporan
)

class CustomAdminSite(admin.AdminSite):
    def login(self, request, extra_context=None):
        if request.method == 'GET' and self.has_permission(request):
            # Jika sudah login, redirect ke buku
            index_path = reverse('admin:perpustakaan_buku_changelist')
            return HttpResponseRedirect(index_path)
        return super().login(request, extra_context)

admin_site = CustomAdminSite(name='myadmin')
admin.site.register(Pengunjung)
admin.site.register(Admin)
admin.site.register(PinjamBuku)
admin.site.register(KembalikanBuku)
admin.site.register(GagalPinjam)
admin.site.register(NotifikasiBerhasil)
admin.site.register(Kategori)
admin.site.register(Peminjaman)
admin.site.register(Laporan)