from django.shortcuts import render
from django.core.cache import cache

from os.path import exists

from .models import UzWord
from .tests import SUFFIXES,BASE_WORDS, predict, generate_dataset, train_model

def add_new_word(word):
    UzWord.objects.create(
        text = word,
        pred_segmentation = word
    )

def segment_view(request):
    if not exists("morph_model.pkl"):
        generate_dataset()
        train_model()
    result = None
    suffix = []
    root = None
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

    return render(request, "index.html", {"root": root, 'suffixes': suffix,
                                           'bazadagi': BASE_WORDS, 'qoshimcha': SUFFIXES})
