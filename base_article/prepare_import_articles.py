# download the data by saving in Google the tab "Fiche article" as csv and rename it as article.csv

# some imports
import os
import shutil
import pandas as pd
import numpy as np
import wget
from PIL import Image
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import base64

# manual part !!!!!
# download page in csv and name it article.csv

# read data file
db_filename = 'Article et fournisseurs - Articles.csv'
db_csv_pd = pd.read_csv(db_filename)

# define number of the article to treat
article_start = 0
article_end = 800

# google authentification
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# define link mat
link_head = "Lien vers photo"
mising_file = 'https://drive.google.com/file/d/15HqdEhGFNL9ycQnL2sJYddhsz56PuwNX'
db_csv_pd[link_head] = db_csv_pd[link_head].fillna(mising_file)
link_mat = db_csv_pd[link_head][article_start:article_end]
name_head = "Nom d'article au Super Cafoutch"
name_mat = db_csv_pd[name_head][article_start:article_end]

# define temp folders
shutil.rmtree('tmp/')
shutil.rmtree('tmp2/')
try : 
    os.makedirs('tmp/')
    os.makedirs('tmp2/')
except: 
    pass

num = 0
base64_mat = []
for link,name in zip(link_mat,name_mat):
    num += 1
    
    # download images
    img_path = 'tmp/{:04d}.img'.format(num)
    if not os.path.exists(img_path):
        if "missing" in link:
            if link.find('id') == -1: link_id = link[link.find('/d/')+3:]
            else: link_id = link[link.find('id=')+3:]
            drive.CreateFile({'id': link_id}).GetContentFile(img_path)
        elif "https://drive.google.com" in link:
            if link.find('id') == -1: link_id = link[link.find('/d/')+3:]
            else: link_id = link[link.find('id=')+3:]
            drive.CreateFile({'id': link_id}).GetContentFile(img_path)
        else:
            wget.download(url = link, out = img_path)

    # convert them to jpg
    jpg_path = 'tmp2/{:04d}.jpg'.format(num)
    try:
        if not os.path.exists(jpg_path):
            Image.open(img_path).convert('RGB').save(jpg_path,'JPEG', quality = 100)
    except:
        print('Error with '+name+' '+link)

    # convert to base64
    with open(jpg_path, "rb") as jpg_file:
        base64_string = base64.b64encode(jpg_file.read())
    base64_mat.append(base64_string)
    
    # save data
dict_label = {'base64': base64_mat}
new_db_csv_pd = pd.DataFrame(dict_label)
new_db_csv_pd = db_csv_pd[article_start:article_end]
new_db_csv_pd.insert(19, "base64", base64_mat, True)
new_db_filename = 'article_with_base64.csv'
new_db_csv_pd.to_csv(new_db_filename, sep=',', encoding='utf-8')