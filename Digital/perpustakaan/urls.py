from django.urls import path
from django.shortcuts import render, redirect
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, LoginView
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from .views import admin_dashboard, generate_laporan

urlpatterns = [
    path('', lambda request: redirect('login_pengunjung'), name='root_redirect'),
    path('home/', views.lihat_daftar_buku, name='home_pengunjung'),
    path('beranda/', views.beranda_pengunjung, name='beranda_pengunjung'),
    path('buku/<str:id_buku>/', views.detail_buku, name='detail_buku'),

    path('pengunjung/register/', views.register_pengunjung, name='register_pengunjung'),
    path('pengunjung/login/', views.login_pengunjung, name='login_pengunjung'),
    path('pengunjung/lupa-password/', views.lupa_password, name='lupa_password'),

    path('dashboard-admin/buku/', views.kelola_buku, name='kelola_buku'),
    path('dashboard-admin/buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('dashboard-admin/buku/edit/<str:id_buku>/', views.edit_buku, name='edit_buku'),
    path('dashboard-admin/buku/hapus/<str:id_buku>/', views.hapus_buku, name='hapus_buku'),

    path('visualisasi/', lambda request: render(request, 'visualisasi.html'), name='visualisasi'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('verifikasi/', views.verifikasi_kode, name='verifikasi_kode'),

    # Custom admin (jika memang ingin dipakai, pastikan tidak bentrok dengan admin bawaan)
    path('admin-custom/', views.admin_custom, name='admin_custom'),
    path('custom-admin/login/', LoginView.as_view(template_name='admin/login.html'), name='admin-login'),
    path('custom-admin/dashboard/', staff_member_required(
        TemplateView.as_view(template_name='admin/dashboard.html')
    ), name='admin-dashboard'),

    # Admin Django bawaan
    path('admin/', admin.site.urls),

    # Fitur buku dan peminjaman
    path('cari-buku/', views.cari_buku, name='cari_buku'),
    path('pinjam-buku/', views.pinjam_buku, name='pinjam_buku'),
    path('kembalikan-buku/', views.kembalikan_buku, name='kembalikan_buku'),
    path('riwayat-peminjaman/', views.lihat_riwayat, name='lihat_riwayat'),
    path('riwayat/', views.lihat_riwayat, name='lihat_riwayat'),
    path('logout/', views.logout, name='logout'),
    path('daftar-buku/', views.lihat_daftar_buku, name='lihat_daftar_buku'),
]