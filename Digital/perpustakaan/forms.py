from django import forms
from .models import Pengunjung, Buku, Laporan

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class RegisterForm(forms.Form):
    nama = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    nomor_anggota = forms.CharField(max_length=100)

class BukuForm(forms.ModelForm):
    class Meta:
        model = Buku
        fields = ['id_buku', 'judul',  'stok']
        widgets = {
            'tahun_terbit': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }

class LaporanForm(forms.ModelForm):
    class Meta:
        model = Laporan
        fields = ['id_laporan', 'tanggal_dibuat', 'jenis', 'isi']
        widgets = {
            'id_laporan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan ID laporan',
            }),
            'tanggal_dibuat': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan tanggal dibuat laporan',
                'type': 'date',
            }),
            'jenis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan jenis laporan'
            }),
            'isi': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan isi laporan',
                'rows': 5
            }),
        }
        labels = {
            'id_laporan': 'ID Laporan',
            'tanggal_dibuat': 'Tanggal Dibuat',
            'jenis': 'Jenis Laporan',
            'isi': 'Isi Laporan'
        }