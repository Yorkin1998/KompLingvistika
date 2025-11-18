import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from main.tests import PATTERNS, medical_phrases, linguistic_phrases
from main.models import Patterns
import re

APOSTROPHES = "[’‘ʼʻʹʽ′`ˈ]"

for i in medical_phrases:
    Patterns.objects.create(word = i, type_of_these = '2')

for i in linguistic_phrases:
    Patterns.objects.create(word = i, type_of_these = '3')

# Barcha patternlarni olib, tekshirib o'zgartirish
for pattern in Patterns.objects.all():
    if re.search(APOSTROPHES, pattern.word):
        # apostroflarni standart ' bilan almashtiramiz
        new_word = re.sub(APOSTROPHES, "'", pattern.word)
        pattern.word = new_word
        pattern.save()  # o'zgartirishlarni saqlaymiz
        print(f"Updated: {new_word}")

