from django.shortcuts import render, redirect, get_object_or_404
from .models import PinjamBuku, Pengunjung
from .forms import LoginForm, RegisterForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.core.mail import send_mail
import random
from django.contrib.auth import authenticate, login

# Halaman utama
def daftar_buku(request):
    daftar_buku = PinjamBuku.objects.all()
    return render(request, 'buku/daftar_buku.html', {'daftar_buku': daftar_buku})

# Detail buku dan pinjam
def detail_buku(request, id_buku):
    buku = get_object_or_404(PinjamBuku, id_buku=id_buku)

    if request.method == 'POST':
        if buku.stok > 0:
            buku.stok -= 1
            buku.save()
            messages.success(request, f"Berhasil meminjam buku: {buku.judul}")
        else:
            messages.error(request, f"Stok habis untuk buku: {buku.judul}")
        return redirect('daftar_buku')

    return render(request, 'buku/detail_buku.html', {'buku': buku})

# Login
def login_pengunjung(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']
        password = request.POST['password']

        # Cek apakah identifier adalah email atau nomor anggota
        try:
            pengunjung = Pengunjung.objects.get(email=identifier)
        except Pengunjung.DoesNotExist:
            try:
                pengunjung = Pengunjung.objects.get(nomor_anggota=identifier)
            except Pengunjung.DoesNotExist:
                pengunjung = None

        if pengunjung is not None:
            user = authenticate(request, username=pengunjung.user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_pengunjung')
            else:
                messages.error(request, 'Password salah.')
        else:
            messages.error(request, 'Email atau Nomor Anggota tidak ditemukan.')

    return render(request, 'pengunjung/login.html')

# Register
def register_pengunjung(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            nomor_anggota = form.cleaned_data['nomor_anggota']

            if Pengunjung.objects.filter(nomor_anggota=nomor_anggota).exists():
                messages.error(request, "Nomor anggota sudah terdaftar. Gunakan nomor lain.")
            else:
                try:
                    hashed_password = make_password(form.cleaned_data['password'])
                    kode = str(random.randint(100000, 999999))
                    pengunjung = Pengunjung.objects.create(
                        nama=form.cleaned_data['nama'],
                        email=email,
                        password=hashed_password,
                        nomor_anggota=nomor_anggota,
                        kode_verifikasi=kode,
                        is_active=False,  # Belum aktif sebelum verifikasi
                    )
                    send_mail(
                        'Kode Verifikasi Akun',
                        f'Kode verifikasi Anda: {kode}',
                        'noreply@perpustakaan.com',
                        [email],
                    )
                    messages.success(request, "Registrasi berhasil! Silakan cek email Anda untuk kode verifikasi.")
                    return redirect(f'/verifikasi/?email={email}')
                except IntegrityError:
                    messages.error(request, "Terjadi kesalahan data. Silakan coba lagi.")
    else:
        form = RegisterForm()
    return render(request, 'pengunjung/register.html', {'form': form})

def verifikasi_kode(request):
    email = request.GET.get('email') or request.POST.get('email')
    if request.method == 'POST':
        kode = request.POST['kode']
        pengunjung = Pengunjung.objects.get(email=email)
        print("Kode di database:", pengunjung.kode_verifikasi)
        print("Kode yang diinput:", kode)
        if pengunjung.kode_verifikasi == kode:
            pengunjung.is_active = True
            pengunjung.kode_verifikasi = ''
            pengunjung.save()
            messages.success(request, 'Verifikasi berhasil. Silakan login.')
            return redirect('login_pengunjung')
        else:
            messages.error(request, 'Kode verifikasi salah.')
    return render(request, 'pengunjung/verifikasi.html', {'email': email})

# Admin – Kelola Buku
def kelola_buku(request):
    daftar_buku = PinjamBuku.objects.all()
    return render(request, 'admin/kelola_buku.html', {'daftar_buku': daftar_buku})

def tambah_buku(request):
    if request.method == 'POST':
        judul = request.POST['judul']
        stok = int(request.POST['stok'])
        id_buku = judul.lower().replace(' ', '-')[:10]
        PinjamBuku.objects.create(id_buku=id_buku, judul=judul, stok=stok)
        return redirect('kelola_buku')
    return render(request, 'admin/kelola_buku.html')

def edit_buku(request, id_buku):
    buku = get_object_or_404(PinjamBuku, id_buku=id_buku)
    if request.method == 'POST':
        buku.judul = request.POST['judul']
        buku.stok = int(request.POST['stok'])
        buku.save()
        return redirect('kelola_buku')
    return render(request, 'admin/kelola_buku.html', {'buku': buku})

def hapus_buku(request, id_buku):
    buku = get_object_or_404(PinjamBuku, id_buku=id_buku)
    buku.delete()
    return redirect('kelola_buku')

def lupa_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Cek apakah email terdaftar
        if Pengunjung.objects.filter(email=email).exists():
            send_mail(
                'Reset Password Perpustakaan Digital',
                'Silakan klik link berikut untuk reset password Anda: ...',
                'noreply@perpustakaan.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Instruksi reset password telah dikirim ke email Anda.')
        else:
            messages.error(request, 'Email tidak terdaftar.')
    return render(request, 'pengunjung/lupaPassword.html')

from perpustakaan.models import PinjamBuku
if not PinjamBuku.objects.filter(id_buku='buku1').exists():
    PinjamBuku.objects.create(id_buku='buku1', judul='Buku Satu', stok=5)

def admin_custom(request):
    return render(request, 'admin.html')