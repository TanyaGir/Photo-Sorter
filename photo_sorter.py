#!/usr/bin/env
import os, os.path
import sys
import requests
from GPSPhoto import gpsphoto
import cv2
from PIL import Image
import pytesseract
import shutil
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def text_count(file_name):
    text = pytesseract.image_to_string(Image.open(file_name))
    return(len(text))


def file_count(givenpath):
    f=[]
    for name in os.listdir(givenpath):
        if os.path.isfile(os.path.join(givenpath, name)):
            imagepath = os.path.join(givenpath, name)
            try:
                im=Image.open(imagepath)
                print("{} is an image file".format(name))
                f.append(imagepath)
                #print(f)
            except IOError:
                print()
    return(f,len(f))


def gps_taginfo(image_path):
    exif = gpsphoto.getGPSData(image_path)
    file_name = (os.path.basename(image_path))
    if exif:
        lat = (exif['Latitude'])
        lng = (exif['Longitude'])
        date = (exif['Date'])
        d = date.split('/')
        year = d[2]
        #print('the latitude is {0}, the longitude is {1} and the year is year {2}' .format(lat,lng,year))
        url = f'https://api.bigdatacloud.net/data/reverse-geocode?latitude={lat}&longitude={lng}8&localityLanguage=en&key=2028335aee824d0ba128d6bcf363abdc'
        response = requests.get(url,timeout=5)
        try:
            country = response.json()["countryName"]
        except KeyError:
            country = "NoData"
        try:
            state = response.json()["principalSubdivision"]
        except KeyError:
            state = "NoData"
        try:
            city = response.json()["locality"]
        except:
            city = "NoData"
        response.close()
        return(file_name,city,state,country,year)
    else:
        print("ERROR:Exif data not present in pic")
        unknown = 'NoExif  Data'
        directory_path = directory_path_maker(image_path,unknown)
        directory_checker(directory_path,image_path)
        return(None,None,None,None,None)

def face_count(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
        )
    #print("Found {0} Faces!".format(len(faces)))
    return(len(faces))

def image_to_text(image_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    #print(image_path_list)
    text = pytesseract.image_to_string(image_path)
    if text:
        count = len(text)
        text = 'Documents'
        directory_path_maker(image_path,text)
        #directory_checker(image_path,)
    else:
        print('no text in the pic')

def directory_checker(dir_path,current_path):
    if os.path.isdir(dir_path):
        print('Directory exists')
        move_file(dir_path,current_path)
    else:
        print('Directory does not exist creating one....')
        os.mkdir(dir_path)
        print('New directory created !')
        move_file(dir_path,current_path)

def directory_checker_mover(numberofpeople,textcount,text_dir_path,family_dir_path,year_dir_path,city_dir_path,current_path):
    if textcount>5:
        if os.path.isdir(text_dir_path):
            move_file(text_dir_path,current_path)
        else:
            os.mkdir(text_dir_path)
            move_file(text_dir_path,current_path)
    else:
        if numberofpeople>0:
            if os.path.isdir(year_dir_path):
                if os.path.isdir(city_dir_path):
                    if os.path.isdir(family_dir_path):
                        move_file(family_dir_path,current_path)
                    else:
                        os.mkdir(family_dir_path)
                        move_file(family_dir_path,current_path)
                else:
                    os.mkdir(city_dir_path)
                    os.mkdir(family_dir_path)
                    move_file(family_dir_path,current_path)
            else:
                os.mkdir(year_dir_path)
                os.mkdir(city_dir_path)
                os.mkdir(family_dir_path)
                move_file(family_dir_path,current_path)
        else:
            if os.path.isdir(year_dir_path):
                if os.path.isdir(city_dir_path):
                    move_file(city_dir_path,current_path)
                else:
                    os.mkdir(city_dir_path)
                    move_file(city_dir_path,current_path)
            else:
                os.mkdir(year_dir_path)
                os.mkdir(city_dir_path)
                move_file(city_dir_path,current_path)

def move_file(dest,source):
    destination = dest
    src = source
    dest = shutil.move(src, destination)

def directory_path_maker(old_path, new_folder_path):
    head_tail = os.path.split(old_path)
    new_path = head_tail[0]
    return(os.path.join(new_path, new_folder_path))

def list_sorter(input_image_list):
    for path in input_image_list:
        #print(path)
        file_name, city, state, country, year = gps_taginfo(path)
        if year is not None:
            print(file_name,city,state,country,year)
            numberofpeople = face_count(path)
            textcount = text_count(path)
            document_folder ="Document"
            text_directory_path = directory_path_maker(path,document_folder)
            year_directory_path = directory_path_maker(path, year)
            empty_folder = "Empty"
            temp_directory_path1 = os.path.join(year_directory_path, empty_folder)
            city_directory_path = directory_path_maker(temp_directory_path1, city)
            temp_directory_path2 = os.path.join(city_directory_path, empty_folder)
            family_folder = 'Family'
            family_directory_path = directory_path_maker(temp_directory_path2,family_folder)
            directory_checker_mover(numberofpeople,textcount,text_directory_path,family_directory_path,year_directory_path,city_directory_path,path)
        else:
            pass

user_input = input("Enter the path of your folder:")
image_file_list , count = file_count(user_input)
print ('The total image file count is {}' .format(count))
list_sorter(image_file_list)

#for path in image_file_list:
    #print(path)
    #file_name, city, state, country, year = gps_taginfo(path)
    #print(file_name,city,state,country,year)
    #face_count(path)
    #image_to_text(path)
    #head_tail = os.path.split(path)
    #new_path = head_tail[0]
    #directory_path = os.path.join(new_path, year)
    #directory_checker(directory_path,path)
