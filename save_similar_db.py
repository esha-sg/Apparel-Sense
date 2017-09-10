from similarity import get_related_products
import pandas as pd
import os
import numpy as np
import pymysql

db = pymysql.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="eshwarsg24",  # your password
                     db="ECom")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need


path_dest = "/home/eshwar/Downloads/tf_files/Apparel_Dataset/results/"
path_bn = "/home/eshwar/Downloads/tf_files/Apparel_Dataset/bottlenecks/"
path_img = "/home/eshwar/Downloads/tf_files/Apparel_Dataset/apparels/"
bneck = "bottlenecks/"
d = "data/"
class_label = ["footwear/", "tshirts/", 'ladieskurta/', 'pants/', 'saree/']


def build_data_frame(path):
    df = pd.read_csv(path, sep=",", header=None)
    numpy_array = df.as_matrix()
    return numpy_array

path = path_dest + bneck
save_path = '/static/data/'
cur = db.cursor()
for i in class_label:
    class_ = i.split('/')[0]
    print('Processing:' + str(i))
    for folder in os.listdir(path + i):
        if folder == 'centroids.csv':
            continue
        print('Processing:' + str(folder))
        features = []
        image_names = []
        p = path + i + folder + '/'
        for fn in os.listdir(p):
            image = os.path.splitext(fn)[0]
            image_id = save_path + class_ + '/' + folder + '/' + image
            try:
                bottleneck = build_data_frame(p + fn)
                related_products = get_related_products(class_, folder, fn)[:3]
                query = 'INSERT INTO similar (image_id, first, second, third) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')' % (image_id, related_products[0], related_products[1], related_products[2])
                cur.execute(query)
                db.commit()
            except:
                pass
db.close()

