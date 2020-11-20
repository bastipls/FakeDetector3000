from django.shortcuts import render
from django.http import HttpResponse
# ML
import pickle
import pandas as pd
import string

from nltk.corpus import stopwords

from langdetect import detect
from django.http import JsonResponse




import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import NoticiaSerializer

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import os


# Directorio de mis mdoelos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELOS_DIR  = os.path.join(BASE_DIR,'modelos/')


def limpiar_stopwrods(noticia):
    idioma = detect(noticia)
    if(idioma == 'en'):
        print('USANDO STOPWRODS INGLES')
        stop = set(stopwords.words('english'))
    elif (idioma == 'es'): 
        print('USANDO STOPWRODS SPANISH')
        stop = set(stopwords.words('spanish'))
    else:
        stop = set(stopwords.words('english'))
  
    punctuation = list(string.punctuation)
    stop.update(punctuation)

    texto_limpio = []
    for i in noticia.split():
        # Si la cadena de texto no esta en la stopwords(stop)
        #Entonces mando la cadena de texto sin las stopwords          
        if i.strip().lower() not in stop:
            texto_limpio.append(i.strip())
    return " ".join(texto_limpio)
def search(noticiaUrl):

    web = noticiaUrl
    req = Request(web, headers={'User-Agent': 'Mozilla/5.0'})
    datos = urlopen(req).read()
    soup =  BeautifulSoup(datos,'html.parser')
    tags = soup.find_all("p")
    title = soup.find("meta",  property="og:title")
    if title:
        texto = title["content"] +' '+ ''.join(str(tag.text) for tag in tags)
    else:
        texto = ''.join(str(tag.text) for tag in tags)
    return texto
def predecir(noticia):
    idioma = detect(noticia)
    print(type(idioma))
    if(idioma == 'en'):
        print('USANDO MODELO INGLES')
        nombre_archivo_modelo = 'randomforestIngles.sav'
        nombre_archivo_transform = 'stringtomatrizIngles.sav'
    elif (idioma == 'es'): 
        print('USANDO MODELO ESPAÑOL')
        nombre_archivo_modelo = 'randomforestEspanol.sav'
        nombre_archivo_transform = 'stringtomatrizEspanol.sav'

    loaded_model = pickle.load(open(MODELOS_DIR+nombre_archivo_modelo, 'rb'))
    load_model_matriz = pickle.load(open(MODELOS_DIR+nombre_archivo_transform, 'rb'))
    # Valido si el string que llega es solo de nuemros
    if noticia.isnumeric():
        return {'cuerpo': False}
        
    # Limpio mi texto de stopwords
    noticia = limpiar_stopwrods(noticia)
    # Paso mi  notica a una serie de pandas
    testdta = pd.Series([noticia])
    # transformo mi noticia a una matriz
    a_predecir = load_model_matriz.transform(testdta)
    # Hago la prediccion de mi noticia
    resultado = loaded_model.predict(a_predecir)
    # Detectar el idioma de la noticia
    

        
    # Transformo a string mi noticia
    prediccion = str(resultado[0])
    json = {'prediccion':prediccion,'idioma':idioma,'cuerpo':noticia}

    return json

def validar_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// O https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #dominio...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ..si es ip
        r'(?::\d+)?' # Esto es opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    resutlado = re.match(regex, url) is not None
    return resutlado
# Get aun no terminado
class prediccion(APIView):
    def options(self,request):
        json = {'post_method':{'cuerpo':'Url o cuerpo de la noticia mas su titulo (Noticias en ingles o español)'},
                'response':{'cuerpo':'Cuerpo de la noticia extraida de la url',
                            'prediccion:':'1 = Verdadero, 0 = Falso',
                            'idioma':'Idioma detectado de la noticia'}}
        return Response(json)
    def post(self, request):

        validar_campos = NoticiaSerializer(data=request.data)

        if validar_campos.is_valid() == False :
            return Response(validar_campos.errors,status=status.HTTP_400_BAD_REQUEST)
        elif  type(request.data['cuerpo'])  != str: 
            return Response({'Error':'El campo [cuerpo] debe ser str'},status=status.HTTP_400_BAD_REQUEST)  
        noticia = request.data['cuerpo']
        if(validar_url(noticia)):
            noticia = search(noticia)
        else:
            noticia = request.data['cuerpo']
        
        json = predecir(noticia)
        my_serializer = NoticiaSerializer(data=json)
        my_serializer.is_valid(True)
        return Response(my_serializer.data) 



