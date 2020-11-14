from django.shortcuts import render
from django.http import HttpResponse
# ML
import pickle
import pandas as pd
from nltk.corpus import stopwords
import string


from langdetect import detect
from django.http import JsonResponse




import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import NoticiaSerializer

def limpiar_stopwrods(dataframe):
    stop = set(stopwords.words('english'))
    punctuation = list(string.punctuation)
    stop.update(punctuation)

    texto_limpio = []
    for i in dataframe.split():
        # Si la cadena de texto no esta en la stopwords(stop)
        #Entonces mando la cadena de texto sin las stopwords          
        if i.strip().lower() not in stop:
            texto_limpio.append(i.strip())
    return " ".join(texto_limpio)
# Metodo para limpiar noticias
def verificar_texto_limpio(texto1,texto2):

    stop = set(stopwords.words('english'))
    punctuation = list(string.punctuation)
    stop.update(punctuation)

    count1 = 0
    stw = list(stop)
    print('Texto con stopwords')
    for i in stw:
        if i in list(texto1.split(" ")):
            print(i)
            count1+=1
    print('Stop words encontradas sin limpiar ',count1)
    #Texto sin stopwords
    print('Texto sin stopwords')
    count2=0
    for i in stw:
        if i in list(texto2.split(" ")):
            print(i)
            count2+=1
    print('Stop words encontradas limpio: ',count2)




def predecir(noticia):
    nombre_archivo_modelo = 'randomforestIngles.sav'
    nombre_archivo_transform = 'stringtomatrizIngles.sav'
    loaded_model = pickle.load(open('./modelos/'+nombre_archivo_modelo, 'rb'))
    load_model_matriz = pickle.load(open('./modelos/'+nombre_archivo_transform, 'rb'))
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
    idioma = detect(noticia)

        
    # Transformo a string mi noticia
    prediccion = str(resultado[0])
    json = {'prediccion':prediccion,'idioma':idioma,'cuerpo':noticia}

    return json


class prediccion(APIView):
    # def get(self,request):
    #     nombre_archivo_modelo = 'randomforestIngles.sav'
    #     nombre_archivo_transform = 'stringtomatrizIngles.sav'
    #     loaded_model = pickle.load(open('./modelos/'+nombre_archivo_modelo, 'rb'))
    #     load_model_matriz = pickle.load(open('./modelos/'+nombre_archivo_transform, 'rb'))
    #     noticia = 'Bitter John McCain Calls Trump ‘Ill Informed’ in Nasty OpEd: ‘We don’t answer to him’What the heck! Senator John McCain just admitted that he doesn t answer to President Trump! Can you imagine if a Senator had done this to Obama? McCain s OpEd in The Washington Post is a horrible hit on Trump. Shame on him!It starts out with a statement about how horrible the white supremacists are and then goes on to discuss Congress getting back to order. It s a snoozer of an OpEd until you get to the last part In a shocking slam on President Trump s character and knowledge of government, McCain shows his bitterness towards Trump. He claims that,  We don t answer to him   but also say that,  We must respect his authority WTH!MCCAIN: IT S TIME CONGRESS RETURNS TO REGULAR ORDER: We can fight like hell for our ideas to prevail. But we have to respect each other or at least respect the fact that we need each other.That has never been truer than today, when Congress must govern with a president who has no experience of public office, is often poorly informed and can be impulsive in his speech and conduct.We must respect his authority and constitutional responsibilities. We must, where we can, cooperate with him. But we are not his subordinates. We don t answer to him. We answer to the American people. We must be diligent in discharging our responsibility to serve as a check on his power. And we should value our identity as members of Congress more than our partisan affiliation.I argued during the health-care debate for a return to regular order, letting committees of jurisdiction do the principal work of crafting legislation and letting the full Senate debate and amend their efforts.We won t settle all our differences that way, but such an approach is more likely to make progress on the central problems confronting our constituents. We might not like the compromises regular order requires, but we can and must live with them if we are to find real and lasting solutions. And all of us in Congress have the duty, in this sharply polarized atmosphere, to defend the necessity of compromise before the American public.SEE WHAT HE DID THERE? He basically said our president is clueless and impulsive so we don t need to listen to him. Unreal! Is McCain bitter and trying to get back at Trump? It s unheard of for a sitting Senator of the party in power trashes the president that is from the same party! Read more: WaPo'
    #     sin_limpiar = noticia
    #     noticia = limpiar_stopwrods(noticia)
    #     testdta = pd.Series([noticia])
    #     a_predecir = load_model_matriz.transform(testdta)
    #     resultado = loaded_model.predict(a_predecir)
    #     # Detectar el idioma de la noticia
    #     idioma = detect(noticia)
    #     prediccion = str(resultado[0])
    #     print('BODY============',request.data)
    #     # print('Lenguaje ',detect(noticia))
    #     # print('Resultado =========== ',resultado[0])
    #     # return HttpResponse('asdasd')
    #     json = {'prediccion':prediccion,'idioma':idioma,'cuerpo':noticia}
    #     my_serializer = NoticiaSerializer(data=json)
    #     my_serializer.is_valid(True)
    
    #     print(type(request.data))
    #     return Response(my_serializer.data)



    def post(self, request):
        validar_campos = NoticiaSerializer(data=request.data)
        if validar_campos.is_valid() == False :
            return Response(validar_campos.errors,status=status.HTTP_400_BAD_REQUEST)
        elif  type(request.data['cuerpo'])  != str: 
            return Response({'Error':'El campo [cuerpo] debe ser str'},status=status.HTTP_400_BAD_REQUEST)  

        json = predecir(request.data['cuerpo'])
        my_serializer = NoticiaSerializer(data=json)
        my_serializer.is_valid(True)
        return Response(my_serializer.data) 



