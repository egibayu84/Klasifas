from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Selamat datang, {user.nama}!', 'success')
            return redirect(url_for('main.index'))
        flash('Email atau password salah.', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not nama or not email or not password:
            flash('Semua field wajib diisi.', 'danger')
            return redirect(url_for('auth.register'))
        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(nama=nama, email=email, password_hash=generate_password_hash(password), peran='pelapor')
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        nama_baru = request.form.get('nama', '').strip()
        password_lama = request.form.get('password_lama', '')
        password_baru = request.form.get('password_baru', '')
        
        if nama_baru:
            current_user.nama = nama_baru
            
        if password_lama and password_baru:
            if len(password_baru) < 6:
                flash('Password baru minimal 6 karakter.', 'danger')
                return redirect(url_for('auth.profil'))
            if check_password_hash(current_user.password_hash, password_lama):
                current_user.password_hash = generate_password_hash(password_baru)
                flash('Password berhasil diubah!', 'success')
            else:
                flash('Password lama salah.', 'danger')
                return redirect(url_for('auth.profil'))
        db.session.commit()
        flash('Profil diperbarui!', 'success')
        return redirect(url_for('auth.profil'))
    return render_template('profil.html')