import os
import shutil
from bs4 import BeautifulSoup

#Listamos directorio raiz ya que ejecutamos dicho script en la carpeta del dataset
for i in os.listdir(path='./Training'):
    #Comprobamos que sea un directorio
    if(os.path.isdir('./Training/'+i) and i!="images2" and i!="labels2"):
        print('Leyendo ./Training/'+i+'/'+i+'.xml')
        infile = open('./Training/'+i+'/'+i+'.xml',"r")
        #infile = open('./MunichCrossroad01/MunichCrossroad01.xml',"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        #Buamos todas las imagenes que contiene el fichero xml
        frames = soup.find_all('frame')
        #Por cada imagen debemos añadir las imagen a ./images/*.png
        #y los labels ./labels/*.txt
        for frame in frames:
            #Eliminamos C:
            pathimageInit=frame.get("file").split(":")[1]
            #Dividimos el path de la imagen para quedarnos con el nombre de esta
            pathimage=pathimageInit.split("/")
            objectlist=frame.find_all('objectlist')
            objects=frame.find_all('object')
            print(len(objects),pathimage)
            #Path de destino de las imagenes y los labels
            datsetImagen='./images/'+pathimage[2]+"_"+pathimage[3]
            datsetlabel='./labelsYoloFormat/'+pathimage[2]+"_"+pathimage[3].split(".")[0]+".txt"
            #Copiamos la imagen del path de origen al path de destino
            shutil.copy("."+pathimageInit, datsetImagen)
            #Fichero para guardar los labls de los objetos
            file = open(datsetlabel, "w")
            #En cada imagen buscamos los objetos que contiene dicha imagen
            for object in objects:
                obj=object.find_all('box')
                for  o in obj:
                    file.write("0 "+ o.get("xc")+" "+ o.get("yc")+" "+o.get("w")+" "+o.get("h")+" "+ os.linesep)
            file.close()
            #print('./'+i+'/'+i+'.xml')
'''
from xml.dom import minidom
#Listamos directorio raiz ya que ejecutamos dicho script en la carpeta del dataset
for i in os.listdir(path='.'):
    #Comprobamos que sea un directorio
    if(os.path.isdir('./'+i)):
        #Contiene el Doc xml donde se especifican la posicion de cada coche en la imagen
        mydoc = minidom.parse('./'+i+'/'+i+'.xml')
        #Listado de todas las las imagenes que contiene el xml y a su vez el directorio
        frame = mydoc.getElementsByTagName('frame')
        for elem in frame:
            #Ruta a la imagen
            pathImage=elem.attributes['file'].value.split(":")[1]
            listpath=pathImage.split('/')
            datsetImagen="./"+listpath[1]+'/images/'+listpath[3]
            #print(elem[0])
            for i in elem.firstChild.firstChild:
                print(i.attributes['file'])
'''
