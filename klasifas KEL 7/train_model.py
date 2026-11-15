import pandas as pd
import re
import joblib
from pathlib import Path
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 1. Setup Sastrawi untuk Preprocessing
stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text

# 2. Dataset Latih yang Diperbanyak (Sesuai 7 Kategori)
data = [
    # Kategori 1: AC & Pendingin
    ("AC tidak dingin", 1), ("AC bocor", 1), ("AC mati", 1), ("ruangan panas", 1),
    ("pendingin rusak", 1), ("AC berisik", 1), ("AC berair", 1), ("AC tidak menyala", 1),
    ("suhu ruangan panas", 1), ("AC kotor", 1), ("filter AC penuh debu", 1), ("AC mengeluarkan bau", 1),
    ("ac tidak dingin di ruang", 1), ("ac mati total", 1), ("pendingin ruangan mati", 1), ("ac bocor berair", 1),
    
    # Kategori 2: Listrik & Penerangan
    ("lampu mati", 2), ("lampu padam", 2), ("stop kontak rusak", 2), ("kabel terkelupas", 2),
    ("lampu berkedip", 2), ("saklar rusak", 2), ("listrik mati", 2), ("lampu koridor mati", 2),
    ("lampu kelas padam", 2), ("stop kontak tidak berfungsi", 2), ("korsleting", 2), ("lampu toilet mati", 2),
    ("lampu koridor lantai mati", 2), ("lampu redup", 2), ("lampu tidak terang", 2), ("listrik turun", 2),
    
    # Kategori 3: Jaringan / Wi-Fi
    ("wifi mati", 3), ("wifi lambat", 3), ("internet putus", 3), ("tidak ada sinyal", 3),
    ("wifi tidak connect", 3), ("jaringan lemot", 3), ("wifi error", 3), ("akses internet lambat", 3),
    ("wifi kampus mati", 3), ("tidak bisa akses wifi", 3), ("jaringan sering putus", 3), ("wifi lemah", 3),
    ("wifi di perpustakaan putus", 3), ("jaringan internet lambat", 3), ("wifi tidak bisa connect", 3), ("sinyal wifi hilang", 3),
    
    # Kategori 4: Kebersihan & Sanitasi
    ("toilet kotor", 4), ("toilet bau", 4), ("air tidak mengalir", 4), ("sampah menumpuk", 4),
    ("lantai kotor", 4), ("toilet tersumbat", 4), ("bak mandi kotor", 4), ("sampah berserakan", 4),
    ("kamar mandi bau", 4), ("air keran mati", 4), ("toilet kotor dan bau", 4), ("sampah tidak diangkut", 4),
    ("air keran wastafel tidak mengalir", 4), ("wastafel mampet", 4), ("toilet kotor bau", 4), ("air tidak keluar", 4),
    
    # Kategori 5: Sarana Kelas
    ("proyektor mati", 5), ("kursi patah", 5), ("meja rusak", 5), ("papan tulis rusak", 5),
    ("proyektor tidak menyala", 5), ("kursi rusak", 5), ("meja goyang", 5), ("papan tulis tidak jelas", 5),
    ("proyektor buram", 5), ("kursi kelas patah", 5), ("meja dosen rusak", 5), ("papan tulis kotor", 5),
    ("proyektor ruang tidak menyala", 5), ("kursi kuliah rusak", 5), ("meja belajar patah", 5), ("layar proyektor rusak", 5),
    
    # Kategori 6: Keamanan & Parkir
    ("parkir gelap", 6), ("pintu gerbang macet", 6), ("motor parkir sembarangan", 6), ("cctv mati", 6),
    ("area parkir rawan", 6), ("pintu kelas rusak", 6), ("keamanan tidak ada", 6), ("parkir sempit", 6),
    ("pagar rusak", 6), ("lampu parkir mati", 6), ("pintu darurat terkunci", 6), ("area parkir kotor", 6),
    ("banyak motor parkir sembarangan", 6), ("parkir liar", 6), ("lampu parkir redup", 6), ("kamera cctv mati", 6),
    
    # Kategori 7: Lainnya
    ("fasilitas olahraga rusak", 7), ("kantin kotor", 7), ("taman tidak terawat", 7), ("lift macet", 7),
    ("masjid kotor", 7), ("lapangan rusak", 7), ("kursi taman rusak", 7), ("fasilitas perpustakaan rusak", 7),
    ("AC perpustakaan mati", 7), ("lampu taman mati", 7), ("tempat sampah rusak", 7), ("pintu masjid rusak", 7),
]

df = pd.DataFrame(data, columns=['teks', 'label'])
print(f"Total data latih: {len(df)}")
df['teks_bersih'] = df['teks'].apply(preprocess_text)

# 3. Split Data (80% Latih, 20% Uji)
X_train, X_test, y_train, y_test = train_test_split(
    df['teks_bersih'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# 4. Bangun Pipeline & Latih Model
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2))),
    ('nb', MultinomialNB(alpha=1.0))
])
pipeline.fit(X_train, y_train)

# 5. Evaluasi Model
y_pred = pipeline.predict(X_test)
print("\n=== EVALUASI MODEL ===")
print(f"Akurasi: {accuracy_score(y_test, y_pred):.2%}")
print(classification_report(y_test, y_pred, zero_division=0))

# 6. Simpan Model (Path Absolut)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "data" / "models" / "model_nb.joblib"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, str(MODEL_PATH))
print(f"Model berhasil disimpan di: {MODEL_PATH}")