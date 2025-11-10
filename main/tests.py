import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

BASE_WORDS = [
    "kitob", "uy", "dost", "bola", "qiz", "oqituvchi", "maktab", "daraxt", "ota", "ona",
    "aka", "uka", "opa", "singil", "dars", "ilm", "fan", "yurt", "xalq", "daryo",
    "tog", "kol", "yol", "shahar", "qishloq", "olma", "anor", "behi", "shaftoli", "uzum",
    "stol", "kursi", "kitobxona", "muallim", "savol", "javob", "xona", "devor", "oyna", "eshik",
    "daftar", "qalam", "telefon", "kompyuter", "dastur", "kod", "soat", "kun", "oy", "yil",
    "bahor", "yoz", "kuz", "qish", "hayot", "dono", "yulduz", "quyosh", "oy"
]

SUFFIXES = [
    "lar", "lari", "miz", "imiz", "ingiz",
    "im", "ing", "i", "ni", "ga", "da", "dan", "ning",
    "man", "san", "siz", "di", "dim", "ding", "dik", "gan", "gach", "gi"
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




# if __name__ == "__main__":
#     # Agar model mavjud bo'lmasa, yangidan quriladi
#     if not os.path.exists("morph_model.pkl"):
#         generate_dataset()
#         train_model()

#     while True:
#         word = input("So'z kiriting (chiqish uchun 'exit'): ")
#         if word == "exit":
#             break
#         root, suffixes = predict(word)
#         print(f"Asos: {root}")
#         if suffixes:
#             print("Qo'shimchalar:", " ".join(suffixes))
#         else:
#             print("Qo'shimcha yo'q")
