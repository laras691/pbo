from django import forms
from .models import Pengunjung
from .models import Buku

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
        fields = ['id_buku', 'judul', 'penulis', 'stok', 'kategori', 'stok', 'cover_url']
        widgets = {
            'tahun_terbit': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }