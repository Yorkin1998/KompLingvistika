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

SUFFIX_TYPES = {
    # Ko‘plik qo‘shimchalari
    "lar": "ko‘plik qo‘shimchasi",

    # Egalik qo‘shimchalari
    "larimiz": "egalik qo‘shimchasi (1-shaxs ko‘plik)",
    "larim": "egalik qo‘shimchasi (1-shaxs birlik)",
    "lari": "egalik qo‘shimchasi (3-shaxs)",
    "miz": "egalik qo‘shimchasi (1-shaxs ko‘plik)",
    "imiz": "egalik qo‘shimchasi (1-shaxs ko‘plik)",
    "ingiz": "egalik qo‘shimchasi (2-shaxs hurmat yoki ko‘plik)",
    "im": "egalik qo‘shimchasi (1-shaxs birlik)",
    "ing": "egalik qo‘shimchasi (2-shaxs birlik)",
    "i": "egalik qo‘shimchasi (3-shaxs)",

    # Kelishik qo‘shimchalari
    "ni": "tushum kelishigi qo‘shimchasi",
    "ga": "yo‘nalish kelishigi qo‘shimchasi",
    "da": "joy kelishigi qo‘shimchasi",
    "dan": "chiqish kelishigi qo‘shimchasi",
    "ning": "qaratqich kelishigi qo‘shimchasi",

    # Fe’l qo‘shimchalari (shaxs/son, zamon)
    "man": "fe’l shaxs-son qo‘shimchasi (1-shaxs birlik)",
    "san": "fe’l shaxs-son qo‘shimchasi (2-shaxs birlik)",
    "siz": "fe’l shaxs-son qo‘shimchasi (2-shaxs hurmat yoki ko‘plik)",
    "di": "fe’l o‘tgan zamon qo‘shimchasi (3-shaxs)",
    "dim": "fe’l o‘tgan zamon qo‘shimchasi (1-shaxs birlik)",
    "ding": "fe’l o‘tgan zamon qo‘shimchasi (2-shaxs birlik)",
    "dik": "fe’l o‘tgan zamon qo‘shimchasi (1-shaxs ko‘plik)",

    # Ravishdosh / fe’l qo‘shimchalari
    "gan": "fe’l sifatdosh qo‘shimchasi",
    "gach": "fe’l ravishdosh qo‘shimchasi (vaqt yoki shart bildiradi)",

    # Boshqalar
    "laridan": "ko‘plik + chiqish kelishigi birikmasi"
}
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
