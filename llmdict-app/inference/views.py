from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Word
import requests
import logging
import json
logger = logging.getLogger('llm-dict')

torchserve_url = "http://localhost:8080/predictions/BERTSentenceEmbedding"

f = open('../key_file.json')    
token = json.loads(f.read())['inference']['key']

from django.views.decorators.csrf import csrf_exempt
def home(request, definition=""):
    if definition:
        data = {"input": definition}
        torchserve_response = requests.get(url = torchserve_url, headers = {'Authorization': "Bearer " + token}, data = data)
        word_ids = [w_id[0] for w_id in torchserve_response.json()]
        top_words = [Word.objects.get(pk=w_id) for w_id in word_ids]
    else:
        top_words = []
    template = loader.get_template("inference/index.html")
    context = {"top_words": top_words, "definition": definition}
    return HttpResponse(template.render(context, request))

def guess(request):
    definition = request.GET["definition"]
    #logger.info("IN GUESS")
    return HttpResponseRedirect(reverse("inference:home_main", args=(definition,)))


