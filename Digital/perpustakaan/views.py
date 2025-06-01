from django.shortcuts import render, redirect, get_object_or_404
from .models import PinjamBuku, Pengunjung, Buku  # pastikan model Buku sudah ada
from .forms import LoginForm, RegisterForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.core.mail import send_mail
import random
from django.contrib.auth import authenticate, login
from .models import Buku, Peminjaman, Pengunjung, Admin, Laporan
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import get_template

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

#Admin - perbaikan ID 
def admin_custom(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        captcha = request.POST.get('captcha')

        # Contoh data admin statis (sebaiknya dari database)
        if admin_id == 'admin' and password == 'admin123' and captcha == '123456':
            messages.success(request, 'Login berhasil!')
            # Redirect ke halaman admin dashboard, misal:
            return redirect('/admin/dashboard/')
        else:
            messages.error(request, 'ID, Password, atau Token salah.')

    return render(request, 'admin/admin_login.html')

# Admin - Dashboard
def admin_dashboard(request):
    # Hitung statistik
    total_buku = Buku.objects.count()
    buku_dipinjam = Peminjaman.objects.filter(status='Dipinjam').count()
    
    # Data untuk chart (contoh: peminjaman 7 hari terakhir)
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

#Admin - Generate Laporan
def generate_laporan(request):
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse('xhtml2pdf belum terinstall. Jalankan: pip install xhtml2pdf')

    if request.method == 'POST':
        jenis_laporan = request.POST.get('jenis_laporan')
        tanggal_mulai = request.POST.get('tanggal_mulai')
        tanggal_selesai = request.POST.get('tanggal_selesai')
        
        # Sesuaikan dengan model Anda
        if jenis_laporan == 'peminjaman':
            data = Peminjaman.objects.filter(
                tanggal_pinjam__gte=tanggal_mulai,
                tanggal_pinjam__lte=tanggal_selesai
            )
        elif jenis_laporan == 'buku':
            data = Buku.objects.all()
        else:  # pengunjung
            data = Pengunjung.objects.all()
        
        context = {
            'data': data,
            'jenis_laporan': jenis_laporan,
            'tanggal_mulai': tanggal_mulai,
            'tanggal_selesai': tanggal_selesai,
            'section': 'laporan',
        }
        
        template = get_template('admin/laporan_pdf.html')
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="laporan_{jenis_laporan}.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF')
        return response
    
    context = {'section': 'laporan'}
    return render(request, 'admin/custom_dashboard.html', context)
    
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

def admin_custom_login(request):
    
    return render(request, 'admin/admin_login.html')
    

def lihat_daftar_buku(request):
    return render(request, 'pengunjung/lihatDaftarBuku.html')

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
    return render(request, 'pengunjung/pinjamBuku.html')

def kembalikan_buku(request):
    pengunjung_id = request.session.get('pengunjung_id')
    if not pengunjung_id:
        return redirect('login_pengunjung')
    pengunjung = Pengunjung.objects.get(id=pengunjung_id)
    daftar_pinjam = Peminjaman.objects.filter(pengunjung=pengunjung, status='Belum Kembali')

    notifikasi_error = None

    if request.method == 'POST':
        judul_buku = request.POST.get('buku')
        # Validasi: cek apakah ada riwayat peminjaman buku ini yang belum dikembalikan
        peminjaman = Peminjaman.objects.filter(
            pengunjung=pengunjung,
            buku__judul=judul_buku,
            status='Belum Kembali'
        ).first()
        if peminjaman:
            # Proses pengembalian (misal update status dan tanggal kembali)
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

    # Buat list riwayat: jika tanggal_kembali kosong, tampilkan "-", jika ada tampilkan tanggalnya
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