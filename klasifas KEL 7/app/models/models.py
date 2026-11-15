from app import db
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    peran = db.Column(db.String(20), default='pelapor')

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    unit_penanggung_jawab = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    pelapor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teks = db.Column(db.Text, nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    kategori_prediksi = db.Column(db.Integer, db.ForeignKey('categories.id'))
    probabilitas = db.Column(db.Float)
    kategori_final = db.Column(db.Integer, db.ForeignKey('categories.id'))
    teknisi = db.Column(db.String(100), nullable=True)
    foto = db.Column(db.String(200), nullable=True) # <-- KOLOM BARU UNTUK FOTO
    status = db.Column(db.String(30), default='Baru')
    waktu_dibuat = db.Column(db.DateTime, default=datetime.utcnow)
    
    pelapor = db.relationship('User', foreign_keys=[pelapor_id])
    kategori_prediksi_rel = db.relationship('Category', foreign_keys=[kategori_prediksi])

class StatusLog(db.Model):
    __tablename__ = 'status_logs'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'))
    status_lama = db.Column(db.String(30))
    status_baru = db.Column(db.String(30))
    petugas_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    waktu = db.Column(db.DateTime, default=datetime.utcnow)
    
    petugas = db.relationship('User', foreign_keys=[petugas_id])