import os
from app import create_app, db  # Tambahkan 'db' di sini

app = create_app()

# KODE BARU: Perintahkan database untuk membuat tabel jika belum ada
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)