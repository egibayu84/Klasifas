from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Complaint
import joblib
import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Setup Sastrawi
stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text

main_bp = Blueprint('main', __name__)

# Path absolut Model
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "data" / "models" / "model_nb.joblib"

if MODEL_PATH.exists():
    MODEL = joblib.load(str(MODEL_PATH))
    print(f"Model dimuat dari {MODEL_PATH}")
else:
    MODEL = None
    print(f"PERINGATAN: Model tidak ditemukan di {MODEL_PATH}")

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/lapor', methods=['GET', 'POST'])
@login_required
def lapor():
    if current_user.peran != 'pelapor':
        flash('Akses ditolak. Hanya Mahasiswa/Dosen yang dapat membuat laporan.', 'danger')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        teks = request.form.get('teks', '').strip()
        lokasi = request.form.get('lokasi', '').strip()
        
        # Validasi
        if not teks or not lokasi:
            flash('Deskripsi dan lokasi wajib diisi.', 'danger')
            return redirect(url_for('main.lapor'))
        if len(teks) < 10:
            flash('Deskripsi keluhan minimal 10 karakter.', 'danger')
            return redirect(url_for('main.lapor'))
        
        # Upload Foto
        nama_file_foto = None
        foto = request.files.get('foto')
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            nama_file_foto = timestamp + filename
            
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            foto.save(os.path.join(upload_folder, nama_file_foto))

        kategori_prediksi = None
        probabilitas = None
        pesan_ai = ""
        
        if MODEL:
            teks_bersih = preprocess_text(teks)
            prediksi = MODEL.predict([teks_bersih])[0]
            proba = MODEL.predict_proba([teks_bersih])[0].max()
            
            if proba >= 0.10: # Threshold rendah untuk demo
                kategori_prediksi = int(prediksi)
                probabilitas = float(proba)
                pesan_ai = f"AI memprediksi Kategori {kategori_prediksi} (keyakinan {probabilitas:.2%})."
            else:
                probabilitas = float(proba)
                pesan_ai = "Keyakinan AI rendah, akan diverifikasi manual oleh admin."
        
        keluhan = Complaint(
            pelapor_id=current_user.id,
            teks=teks,
            lokasi=lokasi,
            kategori_prediksi=kategori_prediksi,
            probabilitas=probabilitas,
            foto=nama_file_foto
        )
        db.session.add(keluhan)
        db.session.commit()
        
        flash(f'Laporan berhasil dikirim! {pesan_ai}', 'success')
        return redirect(url_for('main.laporan_saya'))
        
    return render_template('lapor.html')

@main_bp.route('/laporan-saya')
@login_required
def laporan_saya():
    if current_user.peran != 'pelapor':
        flash('Halaman ini hanya untuk Mahasiswa/Dosen.', 'warning')
        return redirect(url_for('main.index'))

    laporanku = Complaint.query.filter_by(pelapor_id=current_user.id).order_by(Complaint.waktu_dibuat.desc()).all()
    return render_template('laporan_saya.html', laporanku=laporanku)