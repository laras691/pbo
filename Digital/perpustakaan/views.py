from django.shortcuts import render, redirect, get_object_or_404
from .models import Buku, Peminjaman, Pengunjung, Admin, Laporan, PinjamBuku, Kategori
from .forms import LoginForm, RegisterForm, LaporanForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.core.mail import send_mail
import random
from django.http import HttpResponse
from django.template.loader import get_template
from datetime import date
from django.urls import path, reverse

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
        identifier = request.POST.get('identifier')  # email atau nomor anggota
        password = request.POST.get('password')

        # Cari user berdasarkan email atau nomor anggota
        pengunjung = None
        try:
            pengunjung = Pengunjung.objects.get(email=identifier)
        except Pengunjung.DoesNotExist:
            try:
                pengunjung = Pengunjung.objects.get(nomor_anggota=identifier)
            except Pengunjung.DoesNotExist:
                pengunjung = None

        if pengunjung is not None:
            # Cek password hash
            if check_password(password, pengunjung.password):
                # Login berhasil
                request.session['pengunjung_id'] = pengunjung.id
                return redirect('beranda_pengunjung')
            else:
                messages.error(request, 'Password salah. Silakan coba lagi.')
        else:
            messages.error(request, 'Email atau nomor anggota tidak ditemukan.')

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

#Admin custom login
def admin_custom(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        captcha = request.POST.get('captcha')

        if admin_id == 'admin' and password == 'admin123' and captcha == '123456':
            messages.success(request, 'Login berhasil!')
            # Redirect langsung ke halaman admin buku, bukan dashboard
            return redirect(reverse('dashboard_admin'))
        else:
            messages.error(request, 'ID, Password, atau Token salah.')
    return render(request, 'admin/admin.html')

#Admin- dashboard
def dashboard_admin(request):
    return render(request, 'admin/dashboard_admin.html') 

# Admin – Kelola Buku
def kelola_buku(request):
    daftar_buku = PinjamBuku.objects.all()
    return render(request, 'admin/kelola_buku.html', {'daftar_buku': daftar_buku})

def tambah_buku(request):
    if request.method == 'POST':
        id_buku = request.POST['id_buku']  # Pastikan baris ini ada!
        judul = request.POST['judul']
        stok = int(request.POST['stok'])
        PinjamBuku.objects.create(id_buku=id_buku, judul=judul, stok=stok)
        return redirect('kelola_buku')
    return render(request, 'admin/tambah_buku.html')

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

# Admin - kelola kategori
def kelola_kategori(request):
    daftar_kategori = Kategori.objects.all()
    return render(request, 'admin/kelola_kategori.html', {'daftar_kategori': daftar_kategori})

#kelola_pengunjung
def kelola_pengunjung(request):
    # Sementara hanya tampilkan halaman kosong
    return render(request, 'admin/kelola_pengunjung.html')

    return render(request, 'admin/admin_login.html')

#Admin dashboard
def admin_dashboard(request):
    total_buku = Buku.objects.count()
    buku_dipinjam = Peminjaman.objects.filter(status='Dipinjam').count()
    
    from django.db.models.functions import TruncDay
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    hari_ini = datetime.now().date()
    tujuh_hari_lalu = hari_ini - timedelta(days=7)
    
    peminjaman_harian = (
        Peminjaman.objects
        .filter(tanggal_pinjam__gte=tujuh_hari_lalu)
        .annotate(hari=TruncDay('tanggal_pinjam'))
        .values('hari')
        .annotate(jumlah=Count('id'))
        .order_by('hari')
    )
    
    buku_labels = [entry['hari'].strftime('%d %b') for entry in peminjaman_harian]
    buku_data = [entry['jumlah'] for entry in peminjaman_harian]
    
    # Data lainnya
    buku_terbaru = Buku.objects.order_by('-tanggal_ditambahkan')[:5]
    pengunjung_terakhir = Pengunjung.objects.order_by('-terakhir_login')[:5]
    
    context = {
        'total_buku': total_buku,
        'buku_dipinjam': buku_dipinjam,
        'buku_labels': buku_labels,
        'buku_data': buku_data,
        'buku_terbaru': buku_terbaru,
        'pengunjung_terakhir': pengunjung_terakhir,
        'section': 'dashboard',
    }
    return render(request, 'admin/custom_dashboard.html', context)
#Admin daftar-Laporan
def daftar_laporan(request):
    daftar = Laporan.objects.all()
    return render(request, 'admin/daftar_laporan.html', {'daftar': daftar})

#admin - tambah laporan
def tambah_laporan(request):
    if request.method == 'POST':
        form = LaporanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daftar-laporan')
    else:
        form = LaporanForm()
    return render(request, 'admin/tambah_laporan.html', {'form': form})

#admin- cetak Laporan
from django.shortcuts import get_object_or_404, render

def cetak_laporan(request, id_laporan):
    laporan = get_object_or_404(Laporan, id_laporan=id_laporan)
    return render(request, 'admin/laporan_pdf.html', {'laporan': laporan})

# admin edit laporan
from django.shortcuts import get_object_or_404, render, redirect

def edit_laporan(request, id_laporan):
    laporan = get_object_or_404(Laporan, id_laporan=id_laporan)
    if request.method == 'POST':
        form = LaporanForm(request.POST, instance=laporan)
        if form.is_valid():
            form.save()
            return redirect('daftar-laporan')
    else:
        form = LaporanForm(instance=laporan)
    return render(request, 'admin/edit_laporan.html', {'form': form, 'laporan': laporan})

#Admin - Generate Laporan
def generate_laporan(request):
    daftar_laporan = Laporan.objects.all()
    return render(request, 'admin/generate_laporan.html', {'daftar_laporan': daftar_laporan})

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

#lihat Profil
def lihat_profil(request):
<<<<<<< HEAD
    return render(request, 'pengunjung/lihatProfil.html')
    return render(request, 'pengunjung/lihatProfil.html')
=======

    # Jika ingin menampilkan data admin, ambil dari session atau model Admin
    # admin = get_object_or_404(Admin, id_admin=request.session.get('admin_id'))
    # return render(request, 'admin/profil.html', {'admin': admin})
    
>>>>>>> 7255b224e626b2b13f10e21350ed263b08026d84
    return render(request, 'admin/lihat_profil.html')

def edit_profil(request):
    return render(request, 'admin/edit_profil.html')

def ganti_password(request):
    if request.method == 'POST':
        password_lama = request.POST.get('password_lama')
        password_baru = request.POST.get('password_baru')
        
        # Proses ganti password
        pengunjung_id = request.session.get('pengunjung_id')
        pengunjung = get_object_or_404(Pengunjung, id=pengunjung_id)
        
        # Cek password lama
        if check_password(password_lama, pengunjung.password):
            # Ganti dengan password baru
            pengunjung.password = make_password(password_baru)
            pengunjung.save()
            
            # Setelah password berhasil diganti:
            messages.success(request, "Password berhasil diganti!")
            return redirect('beranda_pengunjung')
        else:
            messages.error(request, "Password lama salah.")
    
    return render(request, 'pengunjung/gantiPassword.html')

from django.shortcuts import redirect, get_object_or_404

def hapus_akun(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if request.method == 'POST':
        if pengunjung_id:
            pengunjung = get_object_or_404(Pengunjung, id=pengunjung_id)
            pengunjung.delete()
            request.session.flush()
            messages.success(request, 'Akun Anda berhasil dihapus.')
            return redirect('login_pengunjung')
    return render(request, 'pengunjung/hapusAkun.html')

#Admin custom login
def admin_custom_login(request):
    return render(request, 'admin/admin_login.html')

def lihat_daftar_buku(request):
    daftar_buku = Buku.objects.all()
    return render(request, 'pengunjung/lihatDaftarBuku.html', {'daftar_buku': daftar_buku})

def home_pengunjung(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if not pengunjung_id:
        return redirect('login_pengunjung')
    pengunjung = Pengunjung.objects.get(id=pengunjung_id)

    rekomendasi = Buku.objects.all().order_by('?')[:4]
    kategori = Buku.objects.all()[:6]

    context = {
        'user': pengunjung,
        'rekomendasi': rekomendasi,
        'kategori': kategori,
    }
    return render(request, 'beranda.html', context)

def beranda_pengunjung(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if not pengunjung_id:
        return redirect('login_pengunjung')
    pengunjung = Pengunjung.objects.get(id=pengunjung_id)

    rekomendasi = Buku.objects.all().order_by('?')[:4]
    kategori = Buku.objects.all()[:6]

    context = {
        'user': pengunjung,
        'rekomendasi': rekomendasi,
        'kategori': kategori,
    }
    return render(request, 'beranda.html', context)

def cari_buku(request):
    return render(request, 'cariBuku.html')

def pinjam_buku(request):
    if 'pengunjung_id' not in request.session:
        return redirect('login_pengunjung')
    daftar_buku = Buku.objects.filter(stok__gt=0)
    if request.method == 'POST':
        id_buku = request.POST.get('buku')
        buku = get_object_or_404(Buku, id=id_buku)
        pengunjung = get_object_or_404(Pengunjung, id=request.session['pengunjung_id'])
        if buku.stok > 0:
            buku.stok -= 1
            buku.save()
            Peminjaman.objects.create(
                buku=buku,
                pengunjung=pengunjung,
                tanggal_pinjam=date.today(),
                status='Belum Kembali' 
            )
            messages.success(request, "Peminjaman Berhasil\nBuku berhasil dipinjam. Silakan cek riwayat peminjaman Anda.")
            return redirect('lihat_riwayat')
        else:
            messages.error(request, "Stok buku habis.")
    return render(request, 'pengunjung/pinjamBuku.html', {'daftar_buku': daftar_buku})

def kembalikan_buku(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if not pengunjung_id:
        return redirect('login_pengunjung')
    pengunjung = Pengunjung.objects.get(id=pengunjung_id)
    daftar_pinjam = Peminjaman.objects.filter(pengunjung=pengunjung, status='Belum Kembali')

    notifikasi_error = None

    if request.method == 'POST':
        judul_buku = request.POST.get('buku')
        kode_buku = request.POST.get('kode_buku')
        peminjaman = Peminjaman.objects.filter(
            pengunjung=pengunjung,
            buku__judul=judul_buku,
            buku__kode_buku=kode_buku,
            status='Belum Kembali'
        ).first()
        if peminjaman:
            peminjaman.status = 'Kembali'
            from django.utils import timezone
            peminjaman.tanggal_kembali = timezone.now()
            peminjaman.save()
            return render(request, 'pengunjung/kembalikanBuku.html', {
                'daftar_pinjam': daftar_pinjam,
                'sukses': True,
                'judul_buku': judul_buku
            })
        else:
            notifikasi_error = "Anda tidak memiliki riwayat peminjaman buku tersebut."

    return render(request, 'pengunjung/kembalikanBuku.html', {
        'daftar_pinjam': daftar_pinjam,
        'notifikasi_error': notifikasi_error
    })

def lihat_riwayat(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if not pengunjung_id:
        return redirect('login_pengunjung')
    pengunjung = Pengunjung.objects.get(id=pengunjung_id)
    daftar_pinjam = Peminjaman.objects.filter(pengunjung=pengunjung)

    riwayat = []
    for pinjam in daftar_pinjam:
        riwayat.append({
            'judul': pinjam.buku.judul,
            'tanggal_pinjam': pinjam.tanggal_pinjam,
            'tanggal_kembali': pinjam.tanggal_kembali if pinjam.tanggal_kembali else "-",
            'status': "Kembali" if pinjam.tanggal_kembali else "Belum Kembali"
        })

    return render(request, 'pengunjung/lihatRiwayat.html', {'riwayat': riwayat})

def logout(request):
    request.session.flush()
    return redirect('login_pengunjung')