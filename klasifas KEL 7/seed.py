from app import create_app, db
from app.models.models import User, Category
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabel database berhasil dibuat/dicek.")

    # 1. Akun Admin
    if not User.query.filter_by(email='admin@klasifas.com').first():
        admin = User(
            nama='Admin Sarpras',
            email='admin@klasifas.com',
            password_hash=generate_password_hash('admin123'),
            peran='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Akun Admin berhasil dibuat (admin@klasifas.com / admin123)")
    else:
        print("Akun Admin sudah ada.")

    # 2. Akun Mahasiswa
    if not User.query.filter_by(email='mahasiswa@klasifas.com').first():
        mhs = User(
            nama='Budi Mahasiswa',
            email='mahasiswa@klasifas.com',
            password_hash=generate_password_hash('mhs123'),
            peran='pelapor'
        )
        db.session.add(mhs)
        db.session.commit()
        print("Akun Mahasiswa berhasil dibuat (mahasiswa@klasifas.com / mhs123)")
    else:
        print("Akun Mahasiswa sudah ada.")

    # 3. Kategori
    if not Category.query.first():
        kategori_list = [
            Category(nama='AC & Pendingin', unit_penanggung_jawab='Sarana-prasarana', is_active=True),
            Category(nama='Listrik & Penerangan', unit_penanggung_jawab='Sarana-prasarana', is_active=True),
            Category(nama='Jaringan / Wi-Fi', unit_penanggung_jawab='Unit TIK', is_active=True),
            Category(nama='Kebersihan & Sanitasi', unit_penanggung_jawab='Kebersihan', is_active=True),
            Category(nama='Sarana Kelas', unit_penanggung_jawab='Sarana-prasarana', is_active=True),
            Category(nama='Keamanan & Parkir', unit_penanggung_jawab='Keamanan', is_active=True),
            Category(nama='Lainnya', unit_penanggung_jawab='Admin', is_active=True),
        ]
        db.session.add_all(kategori_list)
        db.session.commit()
        print("7 Kategori berhasil ditambahkan ke database.")