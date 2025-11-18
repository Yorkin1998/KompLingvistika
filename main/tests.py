import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import re
import html

BASE_WORDS = [
    "kitob", "uy", "dost", "bola", "qiz", "oqituvchi", "maktab", "daraxt", "ota", "ona",
    "aka", "uka", "opa", "singil", "dars", "ilm", "fan", "yurt", "xalq", "daryo",
    "tog", "kol", "yol", "shahar", "qishloq", "olma", "anor", "behi", "shaftoli", "uzum",
    "stol", "kursi", "kitobxona", "muallim", "savol", "javob", "xona", "devor", "oyna", "eshik",
    "daftar", "qalam", "telefon", "kompyuter", "dastur", "kod", "soat", "kun", "oy", "yil",
    "bahor", "yoz", "kuz", "qish", "hayot", "dono", "yulduz", "quyosh", "oy"
]

SUFFIXES = [
    "lar",
    "im",
    "ing",
    "i",
    "si",
    "miz",
    "ngiz",
    "ni",
    "ga",
    "qa",
    "da",
    "ta",
    "dan",
    "tan",
    "ning",
    "ningdan",
    "di",
    "dim",
    "ding",
    "dik",
    "gan",
    "man",
    "yapti",
    "yapman",
    "yapsan",
    "yapmiz",
    "yapsiz",
    "adi",
    "arman",
    "arsan",
    "adi",
    "ajak",
    "man",
    "san",
    "miz",
    "siz",
    "lar",
    "ma",
    "mas",
    "may",
    "masa",
    "gin",
    "ing",
    "sin",
    "aylik",
    "chi",
    "lik",
    "kor",
    "dor",
    "li",
    "siz",
    "ona",
    "vchi"
]



def generate_dataset(filename="uzbek_dataset.csv"):
    rows = []
    for root in BASE_WORDS:
        rows.append([root, root, ""])  # plain word

        for suf in SUFFIXES:
            rows.append([root + suf, root, suf])

        for suf1 in SUFFIXES:
            for suf2 in SUFFIXES:
                if suf1 != suf2:
                    word = root + suf1 + suf2
                    rows.append([word, root, f"{suf1} {suf2}"])

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "root", "suffixes"])
        writer.writerows(rows)

    print(f"Dataset generated with {len(rows)} rows → {filename}")


def train_model(dataset_file="uzbek_dataset.csv", model_file="morph_model.pkl"):
    words, roots, suffixes = [], [], []
    with open(dataset_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append(row["word"])
            roots.append(row["root"])
            suffixes.append(row["suffixes"])

    vectorizer = CountVectorizer(analyzer="char", ngram_range=(2, 4))
    X = vectorizer.fit_transform(words)

    clf_root = MultinomialNB()
    clf_root.fit(X, roots)

    clf_suffix = MultinomialNB()
    clf_suffix.fit(X, suffixes)

    joblib.dump((clf_root, clf_suffix, vectorizer), model_file)
    print(f"Model trained and saved → {model_file}")


def split_suffixes(word, root):
    """Qo'shimchalarni bosqichma-bosqich ajratish"""
    suffixes_found = []
    remaining = word[len(root):]
    while remaining:
        matched = False
        for suf in sorted(SUFFIXES, key=lambda x: -len(x)):
            if remaining.startswith(suf):
                suffixes_found.append(suf)
                remaining = remaining[len(suf):]
                matched = True
                break
        if not matched:
            break
    return suffixes_found


def predict(word, model_file="morph_model.pkl"):
    clf_root, clf_suffix, vectorizer = joblib.load(model_file)
    if word not in BASE_WORDS:
        if word not in BASE_WORDS:

            remaining = word
            suffixes_found = []

            # suffixlarni oxiridan boshlab qirqamiz
            while True:
                matched = False
                for suf in sorted(SUFFIXES, key=lambda x: -len(x)):
                    if remaining.endswith(suf):
                        suffixes_found.insert(0, suf)
                        remaining = remaining[:-len(suf)]
                        matched = True
                        break
                if not matched:
                    break

            root = remaining
            return root, suffixes_found
    else:
        X = vectorizer.transform([word])
        predicted_root = clf_root.predict(X)[0]

    # Agar model topgan root bazada bo'lmasa → model natijasini ishlatmaymiz
    

    # Agar model natijasi to'g'ri bo'lsa → modelni ishlatamiz
    root = predicted_root
    suffixes = split_suffixes(word, root)
    return root, suffixes





PATTERNS = [
"Axborot texnologiyalari",
"Sun'iy intellekt",
"Ma'lumotlar bazasi",
"Kompyuter tarmoqlari",
"Bulutli hisoblash",
"Dasturiy ta’minot",
"Operatsion tizim",
"Ma’lumotlarni qayta ishlash",
"Kiberxavfsizlik",
"Axborot tizimi",
"Veb-ilova",
"Ma’lumotlarni saqlash",
"Sun’iy neyron tarmoq",
"Ma’lumotlar tahlili",
"Katta ma’lumotlar (Big Data)",
"Raqamli transformatsiya",
"Ma’lumotlarni vizualizatsiya qilish",
"Robototexnika",
"Internet of Things (IoT)",
"Mobil ilovalar",
"Ma’lumotlarni uzatish",
"Bulutli xizmatlar",
"Kriptovalyuta texnologiyasi",
"Blokcheyn",
"Shifrlash algoritmi",
"Ma’lumotlarni tiklash",
"Ma’lumotlar xavfsizligi",
"Sun’iy ong",
"Kompyuter grafikasi",
"Virtual reallik",
"Kengaytirilgan reallik",
"Dasturlash tillari",
"Ma’lumotlar oqimi",
"Tarmoq protokollari",
"Internet xavfsizligi",
"Ma’lumotlarni qayta ishlash tizimi",
"Axborot tizimi menejmenti",
"Server infratuzilmasi",
"Veb-sayt dizayni",
"Ma’lumotlar bazasi boshqaruvi",
"Mashina o‘rganish",
"Algoritmik tahlil",
"Sun’iy intellekt tizimi",
"Dasturiy modul",
"Elektron tijorat",
"Raqamli marketing",
"Ma’lumotlar arxivi",
"Server xotirasi",
"Kompyuter tarmog‘i",
"Ma’lumotlarni kodlash",
"Internet ilovalari",
"Mobil texnologiyalar",
"Kompyuter tizimi",
"Bulutli server",
"Raqamli axborot",
"Ma’lumotlarni optimizatsiya qilish",
"Ma’lumotlarni himoya qilish",
"Veb-server",
"Tarmoq xavfsizligi",
"Elektron pochta tizimi",
"Dasturiy platforma",
"Sun’iy intellekt algoritmlari",
"Ma’lumotlarni indekslash",
"Ma’lumotlarni tozalash",
"Internet protokoli",
"Kompyuter tahlili",
"Axborot oqimi",
"Kompyuter arxitekturasi",
"Raqamli tizim",
"Ma’lumotlar tahlilchisi",
"Sun’iy neyron algoritmi",
"Elektron ma’lumotlar",
"Dasturiy interfeys",
"Veb-dastur",
"Kompyuter xavfsizligi",
"Ma’lumotlar zaxirasi",
"Raqamli kommunikatsiya",
"Server konfiguratsiyasi",
"Ma’lumotlarni avtomatlashtirish",
"Kompyuter dasturi",
"Tarmoq monitoringi",
"Axborot texnologiyalari menejmenti",
"Ma’lumotlarni qayta ishlash texnologiyasi",
"Internet tarmog‘i",
"Sun’iy intellekt platformasi",
"Ma’lumotlarni vizualizatsiya qilish vositasi",
"Kompyuter tizimlari integratsiyasi",
"Raqamli texnologiyalar",
"Bulutli platforma",
"Ma’lumotlarni yig‘ish",
"Ma’lumotlarni tahlil qilish vositasi",
"Tarmoq serveri",
"Dasturiy ta’minot yechimi",
"Sun’iy intellekt modeli",
"Ma’lumotlar oqimi tahlili",
"Internet ilovalarining xavfsizligi",
"Kompyuter infratuzilmasi",
"Axborot xavfsizligi protokoli",
"Ma’lumotlarni saqlash tizimi",
"Raqamli transformatsiya strategiyasi",
]


import re
import html

# Barcha turdagi apostrof belgilar
APOSTROPHES = "['’‘ʼʻʹʽ′`ˈ]"

def normalize_pattern(p):
    p = p.lower()
    p = re.sub(APOSTROPHES, "'", p)
    p = p.replace("-", " ")
    return p

def build_flexible_regex(pattern):
    """
    "Sun’iy intellekt" => flexible regex
    Sun[apostrof, defis, probel]*iy[\s'\-’]*intellekt[a-zA-Zа-яА-Яʼ‘’'`\-]*
    """
    pattern_norm = normalize_pattern(pattern)
    parts = pattern_norm.split()
    if len(parts) > 1:
        # bir necha so'z bo'lsa ularni bo'shliq, defis yoki apostrof orqali bog'lash
        regex = rf"(?:[\s{APOSTROPHES}\-])*".join(map(re.escape, parts))
    else:
        regex = re.escape(parts[0])
    # So'ngida qo‘shimchalar uchun (o‘zbekcha, ruscha) harflar
    regex += r"[a-zA-Zа-яА-Яʼ‘’'`\-]*"
    return regex

def highlight_text(text, patterns):
    if not text:
        return ""

    safe = html.escape(text)
    regexes = [build_flexible_regex(p) for p in sorted(patterns, key=len, reverse=True)]
    combined = "|".join(regexes)
    # (?iu): case-insensitive + Unicode aware
    regex = re.compile(r"(?iu)\b(" + combined + r")\b")

    def repl(m):
        return f'<span class="highlight">{m.group(0)}</span>'

    highlighted = regex.sub(repl, safe)
    return highlighted