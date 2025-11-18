from django.shortcuts import render
from django.core.cache import cache
from django import forms
from .tests import highlight_text, PATTERNS
from os.path import exists

from .models import UzWord, UmumiyTurkum, Patterns
from .tests import SUFFIXES,BASE_WORDS, predict, generate_dataset, train_model

import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from django.shortcuts import render
import re

def add_new_word(word):
    UzWord.objects.create(
        text = word,
        pred_segmentation = word
    )

def parse_word_classes(result_html):
    soup = BeautifulSoup(result_html, "html.parser")
    data = {}

    # Har bir kartani topamiz
    for card in soup.select(".card-body"):
        spans = card.find_all("span")
        if len(spans) >= 2:
            # 1-span — so‘z, 2-span — turkum
            word = spans[0].get_text(strip=True)
            pos = spans[1].get_text(strip=True)
            # Masalan [Ot] -> Ot
            pos = pos.strip("[]")
            data[word] = pos

    return data

SUFFIX_TYPES = {
    "lar": "ko‘plik qo‘shimchasi",

    "im": "egalik (1-shaxs birlik)",
    "ing": "egalik (2-shaxs birlik)",
    "i": "egalik (3-shaxs)",
    "si": "egalik 3-shaxs variant",

    "miz": "egalik (1-shaxs ko‘plik)",
    "ngiz": "egalik (2-shaxs ko‘plik yoki hurmat)",

    "ni": "tushum kelishigi",
    "ga": "yo‘nalish kelishigi",
    "qa": "yo‘nalish fonetik variant",
    "da": "joy kelishigi",
    "ta": "joy kelishigi fonetik variant",
    "dan": "chiqish kelishigi",
    "tan": "chiqish fonetik variant",
    "ning": "qaratqich kelishigi",
    "ningdan": "birikma ko‘rinishi",

    "di": "o‘tgan zamon (3-shaxs)",
    "dim": "o‘tgan zamon (1-shaxs birlik)",
    "ding": "o‘tgan zamon (2-shaxs birlik)",
    "dik": "o‘tgan zamon (1-shaxs ko‘plik)",
    "gan": "sifatdosh",
    "man": "tasdiq",

    "yapti": "hozirgi zamon davom (3-shaxs)",
    "yapman": "hozirgi zamon davom (1-shaxs)",
    "yapsan": "hozirgi zamon davom (2-shaxs)",
    "yapmiz": "hozirgi zamon davom (1-shaxs ko‘plik)",
    "yapsiz": "hozirgi zamon davom (hurmat)",

    "adi": "kelasi zamon taxminiy",
    "arman": "kelasi zamon ehtimol (1-shaxs)",
    "arsan": "kelasi zamon ehtimol (2-shaxs)",
    "adi": "kelasi zamon (3-shaxs)",
    "ajak": "kelasi zamon (qadimiy/kitobiy)",

    "man": "1-shaxs birlik",
    "san": "2-shaxs birlik",
    "miz": "1-shaxs ko‘plik",
    "siz": "2-shaxs hurmat/ko‘plik",
    "lar": "3-shaxs ko‘plik hurmat",

    "ma": "bo‘lishsizlik",
    "mas": "bo‘lishsizlik (kelasi zamon/reja)",
    "may": "bo‘lishsizlik (hozirgi zamon)",
    "masa": "shart mayli bo‘lishsizlik",

    "gin": "iliy buyruq miniatyur shakl",
    "ing": "hurmatli buyruq",
    "sin": "3-shaxs buyruq",
    "aylik": "1-shaxs ko‘plik buyruq",

    "chi": "kasb, nisbat (haydovchi, o‘qituvchi)",
    "lik": "sifat/ot yasovchi (yaxshilik, do‘stlik)",
    "kor": "xususiyat bildiradi (shodkor, uddaburon)",
    "dor": "egalik/sohiblik (ilm-dor)",
    "li": "sifat yasovchi (uyli, belgilangan)",
    "siz": "inkor/yo‘qlik (uy-siz, imkon-siz)",
    "ona": "nisbat, ayollik (kuyovona)",
    "vchi": "fe’llardan ot yasalishi",
}
APOSTROPHES = "[’'’‘ʼʻʹʽ′`ˈ]"

def segment_view(request):
    if not exists("morph_model.pkl"):
        generate_dataset()
        train_model()

    result_html = None
    suffixes_with_type = []
    root = None
    word_class_final = None

    if request.method == "POST":
        word = request.POST.get("word")
        if word:
            root, found_suffixes = predict(word)
            if found_suffixes:
                for s in found_suffixes:
                    suffixes_with_type.append({
                        "suffix": s,
                        "type": SUFFIX_TYPES.get(s, "Noma’lum turdagi qo‘shimcha")
                    })
            else:
                suffixes_with_type = [{"suffix": "Mavjud emas!", "type": ""}]

            # 2️⃣ Endi ildiz (root) bazada bor-yo‘qligini tekshiramiz
            mavjud_turkum = None
            if root:
                mavjud_turkum = UmumiyTurkum.objects.filter(word__iexact=root).first()

            if mavjud_turkum:
                # Agar ildiz bazada bo‘lsa, shu turkumdan foydalanamiz
                turkum_nomi = dict(UmumiyTurkum.TURKUM).get(mavjud_turkum.type_is, "Noma’lum turkum")
                word_class_final = f"{turkum_nomi} (bazadan olindi)"
            else:
                # 3️⃣ Aks holda — korpus orqali aniqlaymiz va bazaga yozamiz
                text = root or word
                tmp_dir = tempfile.mkdtemp()
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"--user-data-dir={tmp_dir}")
                driver = webdriver.Chrome(options=options)

                try:
                    driver.get("https://uznatcorpara.uz/uz/POSTag")

                    text_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "text"))
                    )
                    text_field.clear()
                    text_field.send_keys(text)

                    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    submit_button.click()

                    collapse = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "collapseTwo"))
                    )

                    result_html = collapse.get_attribute("outerHTML")
                    word_classes = parse_word_classes(result_html)

                    if word_classes:
                        first_class = list(word_classes.values())[0]
                        if "Ot" in first_class:
                            word_class_final = "Ot (ot so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='1')
                        elif "Sifat" in first_class:
                            word_class_final = "Sifat (sifat so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='2')
                        elif "Son" in first_class:
                            word_class_final = "Son (son so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='3')
                        elif "Fe’l" in first_class or "Fe'l" in first_class:
                            word_class_final = "Fe’l (fe’l so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='4')
                        elif "Ravish" in first_class:
                            word_class_final = "Ravish (ravish so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='5')
                        elif "Olmosh" in first_class:
                            word_class_final = "Olmosh (olmosh so‘z turkumi)"
                            UmumiyTurkum.objects.create(word=text, type_is='6')
                        else:
                            word_class_final = "Noaniq turkum"
                    else:
                        word_class_final = "Noaniq turkum"

                except Exception as e:
                    result_html = f"<p style='color:red;'>Xatolik yuz berdi: {e}</p>"
                    word_class_final = "Noaniq turkum"
                finally:
                    driver.quit()

    return render(request, "index.html", {
        "root": root,
        "suffixes": suffixes_with_type,
        "word_class": word_class_final,
        "bazadagi": BASE_WORDS,
        "qoshimcha": SUFFIX_TYPES,
    })
 
# Ranglar har bir type_of_these uchun
HIGHLIGHT_COLORS = {
    '1': '#ffadad',  # Texnik - qizil rang
    '2': '#caffbf',  # Meditsina - yashil
    '3': '#9bf6ff',  # Filologik - ko‘k
}

TYPE_LABELS = {
    '1': 'Texnik ibora',
    '2': 'Meditsina ibora',
    '3': 'Filologik ibora',
}


def highlight_matches(request):
    highlighted_text = ''
    detected_words = []

    if request.method == 'POST':
        input_text = request.POST.get('input_text', '')
        patterns = Patterns.objects.all()  # word + type_of_these

        for pattern_obj in patterns:
            word = pattern_obj.word
            type_of = pattern_obj.type_of_these

            # Apostroflarni turli belgilar bilan moslash
            pattern_regex = re.sub("['’‘ʼʻʹʽ′`ˈ]", APOSTROPHES, word)

            regex = re.compile(pattern_regex, flags=re.IGNORECASE)

            if re.search(regex, input_text):
                detected_words.append(word)
                color = HIGHLIGHT_COLORS.get(type_of, '#ffff00')  # default yellow
                label = TYPE_LABELS.get(type_of, 'Predmet ibora')

                # Highlight qilish va tooltip qo‘yish
                input_text = re.sub(
                    regex,
                    rf'<mark style="background-color:{color};" title="{label}">\g<0></mark>',
                    input_text
                )

        highlighted_text = input_text

    all_patterns = Patterns.objects.all()

    context = {
        'highlighted_text': highlighted_text,
        'detected_words': detected_words,
        'patterns': all_patterns
    }

    return render(request, 'analyze.html', context)