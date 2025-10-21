from django.shortcuts import render
from django.core.cache import cache

from os.path import exists

from .models import UzWord
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

def segment_view(request):
    if not exists("morph_model.pkl"):
        generate_dataset()
        train_model()
    result_html = None
    suffix = []
    root = None
    word_classes = None
    if request.method == "POST":
        word = request.POST.get("word")
        if word:
            if word not in BASE_WORDS:
                add_new_word(word)
            root, suffixes = predict(word)
            if suffixes:
                suffix = suffixes
            else:
                suffix = ["Mavjud emas!"]

            text = request.POST.get('word')
        
            tmp_dir = tempfile.mkdtemp()
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--user-data-dir={tmp_dir}")

            driver = webdriver.Chrome(options=options)

            try:
                driver.get("https://uznatcorpara.uz/uz/POSTag")

                # Text field ni topamiz va matn yuboramiz
                text_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "text"))
                )
                text_field.clear()
                text_field.send_keys(text)

                # Submit bosamiz
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()

                # collapseTwo bo‘limini kutamiz
                collapse = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "collapseTwo"))
                )

                # Faqat collapseTwo ichidagi HTML ni olamiz
                result_html = collapse.get_attribute("outerHTML")
                word_classes = parse_word_classes(result_html)

            except Exception as e:
                result_html = f"<p style='color:red;'>Xatolik yuz berdi: {e}</p>"
                word_classes = None
            finally:
                driver.quit()
    return render(request, "index.html", {"root": root, 'suffixes': suffix,
                                           'bazadagi': BASE_WORDS, 'qoshimcha': SUFFIXES, 'result_html': word_classes})
