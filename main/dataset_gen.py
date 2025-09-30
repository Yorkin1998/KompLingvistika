import csv

BASE_WORDS = [
    "kitob", "uy", "dost", "bola", "qiz", "oqituvchi", "maktab", "daraxt", "ota", "ona",
    "aka", "uka", "opa", "singil", "dars", "ilm", "fan", "yurt", "xalq", "daryo",
    "tog", "kol", "yol", "shahar", "qishloq", "olma", "anor", "behi", "shaftoli", "uzum",
    "stol", "kursi", "kitobxona", "muallim", "savol", "javob", "xona", "devor", "oyna", "eshik",
    "daftar", "qalam", "telefon", "kompyuter", "dastur", "kod", "soat", "kun", "oy", "yil",
    "bahor", "yoz", "kuz", "qish", "hayot", "dono", "yulduz", "quyosh", "oy"
]

SUFFIXES = [
    "lar", "larimiz", "larim", "lari", "laridan", "miz", "imiz", "ingiz",
    "im", "ing", "i", "ni", "ga", "da", "dan", "ning",
    "man", "san", "siz", "di", "dim", "ding", "dik", "gan", "gach"
]


def generate_dataset(filename="uzbek_dataset.csv", limit_per_root=30):
    """
    Generate dataset with structure: word, root, suffixes (space separated if multiple)
    """
    rows = []
    for root in BASE_WORDS:
        # plain word
        rows.append([root, root, ""])

        # generate combinations with suffixes
        for suf in SUFFIXES:
            rows.append([root + suf, root, suf])

        # generate 2-suffix combos (example: lar + dan)
        for suf1 in SUFFIXES:
            for suf2 in SUFFIXES:
                if suf1 != suf2 and len(rows) < limit_per_root:
                    word = root + suf1 + suf2
                    rows.append([word, root, f"{suf1} {suf2}"])

    # save to csv
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "root", "suffixes"])
        writer.writerows(rows)

    print(f"Dataset generated with {len(rows)} rows → {filename}")


if __name__ == "__main__":
    generate_dataset()
