from django.shortcuts import render
from django.core.cache import cache

from os.path import exists

from .models import UzWord, OT, SIFAT
from .tests import SUFFIXES,BASE_WORDS, predict, generate_dataset, train_model

import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

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
    "lari": "egalik qo‘shimchasi (3-shaxs)",
    "miz": "egalik qo‘shimchasi (1-shaxs ko‘plik)",
    "imiz": "egalik qo‘shimchasi (1-shaxs ko‘plik)",
    "ingiz": "egalik qo‘shimchasi (2-shaxs hurmat yoki ko‘plik)",
    "im": "egalik qo‘shimchasi (1-shaxs birlik)",
    "ing": "egalik qo‘shimchasi (2-shaxs birlik)",
    "i": "egalik qo‘shimchasi (3-shaxs)",
    "ni": "tushum kelishigi qo‘shimchasi",
    "ga": "yo‘nalish kelishigi qo‘shimchasi",
    "da": "joy kelishigi qo‘shimchasi",
    "dan": "chiqish kelishigi qo‘shimchasi",
    "ning": "qaratqich kelishigi qo‘shimchasi",
    "man": "fe’l shaxs-son qo‘shimchasi (1-shaxs birlik)",
    "san": "fe’l shaxs-son qo‘shimchasi (2-shaxs birlik)",
    "siz": "fe’l shaxs-son qo‘shimchasi (2-shaxs hurmat yoki ko‘plik)",
    "di": "fe’l o‘tgan zamon qo‘shimchasi (3-shaxs)",
    "dim": "fe’l o‘tgan zamon qo‘shimchasi (1-shaxs birlik)",
    "ding": "fe’l o‘tgan zamon qo‘shimchasi (2-shaxs birlik)",
    "dik": "fe’l o‘tgan zamon qo‘shimchasi (1-shaxs ko‘plik)",
    "gan": "fe’l sifatdosh qo‘shimchasi",
    "gach": "fe’l ravishdosh qo‘shimchasi (vaqt yoki shart bildiradi)",
}

def segment_view(request):
    if not exists("morph_model.pkl"):
        generate_dataset()
        train_model()

    result_html = None
    suffixes = []
    root = None
    word_classes = None
    suffixes_with_type = []
    word_class_final = None  # bu bizning filtrlangan natija

    if request.method == "POST":
        word = request.POST.get("word")
        if word:
            if word not in BASE_WORDS:
                add_new_word(word)

            root, found_suffixes = predict(word)

            if found_suffixes:
                suffixes = found_suffixes
                for s in suffixes:
                    suffixes_with_type.append({
                        "suffix": s,
                        "type": SUFFIX_TYPES.get(s, "Noma’lum turdagi qo‘shimcha")
                    })
            else:
                suffixes_with_type = [{"suffix": "Mavjud emas!", "type": ""}]

            text = word

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
                    # 1-so‘zning turkumini olamiz
                    first_class = list(word_classes.values())[0]

                    if "Ot" in first_class:
                        word_class_final = "Ot (ot so‘z turkumi)"
                        if OT.objects.filter(word = word).exists():
                            pass
                        else:
                            OT.objects.create(
                                word = word
                            )
                    elif "Sifat" in first_class:
                        if SIFAT.objects.filter(word = word).exists():
                            pass
                        else:
                            SIFAT.objects.create(
                                word = word
                            )
                        word_class_final = "Sifat (sifat so‘z turkumi)"
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
        "bazadagi": BASE_WORDS,
        "qoshimcha": SUFFIX_TYPES,
        "word_class": word_class_final  
    })
