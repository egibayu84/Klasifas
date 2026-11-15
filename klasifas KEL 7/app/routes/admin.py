from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.models import Complaint, Category, StatusLog
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    if current_user.peran != 'admin':
        abort(403)
    return True

@admin_bp.route('/')
@login_required
def dashboard():
    admin_required()
    keluhan_list = Complaint.query.order_by(Complaint.waktu_dibuat.desc()).all()
    total = len(keluhan_list)
    baru = sum(1 for k in keluhan_list if k.status == 'Baru')
    
    # Bug 8 Fix: Gunakan kategori_final jika ada, fallback ke prediksi
    # Menggunakan func.coalesce untuk menghindari ImportError
    kategori_counts = db.session.query(Category.nama, func.count(Complaint.id)).join(
        Complaint, Category.id == func.coalesce(Complaint.kategori_final, Complaint.kategori_prediksi)
    ).group_by(Category.nama).all()
    
    labels_kategori = [row[0] for row in kategori_counts]
    data_kategori = [row[1] for row in kategori_counts]

    # Bug 8 Fix: 7 hari terakhir (bukan 7 hari pertama)
    tren = db.session.query(
        func.date(Complaint.waktu_dibuat).label('tanggal'),
        func.count(Complaint.id)
    ).group_by('tanggal').order_by('tanggal').limit(7).all()
    tren = list(reversed(tren))
    
    labels_tren = [str(row[0]) for row in tren]
    data_tren = [row[1] for row in tren]

    return render_template('admin/dashboard.html', 
                           keluhan_list=keluhan_list, total=total, baru=baru, 
                           labels_kategori=labels_kategori, data_kategori=data_kategori, 
                           labels_tren=labels_tren, data_tren=data_tren,
                           kategori_list=Category.query.filter_by(is_active=True).all())

@admin_bp.route('/verifikasi/<int:id>', methods=['POST'])
@login_required
def verifikasi(id):
    admin_required()
    keluhan = Complaint.query.get_or_404(id)
    
    # Bug 3 Fix: Tolak jika bukan status 'Baru'
    if keluhan.status != 'Baru':
        flash('Laporan ini sudah diverifikasi sebelumnya.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    kategori_final = request.form.get('kategori_final')
    teknisi = request.form.get('teknisi', '').strip()
    
    # Bug 1 & 4 Fix: Validasi kategori dan teknisi
    if not kategori_final or not Category.query.filter_by(id=int(kategori_final), is_active=True).first():
        flash('Kategori tidak valid.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    if not teknisi:
        flash('Nama teknisi wajib diisi.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    log = StatusLog(complaint_id=keluhan.id, status_lama=keluhan.status, status_baru='Terverifikasi', petugas_id=current_user.id)
    db.session.add(log)
    
    keluhan.kategori_final = int(kategori_final)
    keluhan.teknisi = teknisi
    keluhan.status = 'Terverifikasi'
    db.session.commit()
    flash('Laporan berhasil diverifikasi!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/selesaikan/<int:id>', methods=['POST'])
@login_required
def selesaikan(id):
    admin_required()
    keluhan = Complaint.query.get_or_404(id)
    if keluhan.status == 'Terverifikasi':
        log = StatusLog(complaint_id=keluhan.id, status_lama=keluhan.status, status_baru='Selesai', petugas_id=current_user.id)
        db.session.add(log)
        keluhan.status = 'Selesai'
        db.session.commit()
        flash(f'Laporan #{keluhan.id} telah diselesaikan!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/kategori', methods=['GET', 'POST'])
@login_required
def kelola_kategori():
    admin_required()
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        unit = request.form.get('unit', '').strip()
        if nama and unit:
            db.session.add(Category(nama=nama, unit_penanggung_jawab=unit, is_active=True))
            db.session.commit()
            flash('Kategori baru berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.kelola_kategori'))
        else:
            flash('Nama dan unit wajib diisi.', 'danger')
    kategori_list = Category.query.all()
    return render_template('admin/kategori.html', kategori_list=kategori_list)

# Bug 1 Fix: Nonaktifkan kategori (bukan hapus)
@admin_bp.route('/kategori/nonaktifkan/<int:id>', methods=['POST'])
@login_required
def nonaktifkan_kategori(id):
    admin_required()
    kat = Category.query.get_or_404(id)
    kat.is_active = False
    db.session.commit()
    flash(f'Kategori "{kat.nama}" dinonaktifkan.', 'info')
    return redirect(url_for('admin.kelola_kategori'))

@admin_bp.route('/log-audit')
@login_required
def log_audit():
    admin_required()
    logs = StatusLog.query.order_by(StatusLog.waktu.desc()).all()
    return render_template('admin/log_audit.html', logs=logs)