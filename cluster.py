from time import time
import pandas as pd
import shutil
from sklearn.externals import joblib
from sklearn.cluster import KMeans
import os
import numpy as np
from sklearn.metrics import silhouette_score
from numpy import genfromtxt

path_dest = "/home/gautham/Downloads/tf_files/Apparel_Dataset/results/"
path_bn = "/home/gautham/Downloads/tf_files/Apparel_Dataset/bottlenecks/"
path_img = "/home/gautham/Downloads/tf_files/Apparel_Dataset/apparels/"
bneck = "bottlenecks/"
d = "data/"
class_label = ["footwear/", "tshirts/", 'ladieskurta/', 'pants/', 'saree/']


def build_data_frame(path):
    df = pd.read_csv(path, sep=",", header=None)
    numpy_array = df.as_matrix()
    return numpy_array


# init1 = build_data_frame(path_bn+class_label+'11452153280145-Hush-Puppies-Men-Formal-Shoes-1691452153278975-1_mini.jpg.txt')
# init2 = build_data_frame(path_bn+class_label+'Sole-Threads-Kids-Yellow--Navy-Beach-Printed-Flip-Flops_1_7cb901185f3511b444bad579c12c8abf_mini.jpg.txt')
# init3 = build_data_frame(path_bn+class_label+'11447153884540-ASICS-Men-Sports-Shoes-311447153884127-1_mini.jpg.txt')
# init4 = build_data_frame(path_bn+class_label+'11462171632955-Shoetopia-Women-Flats-9141462171632759-1_mini.jpg.txt')
# init5 = build_data_frame(path_bn+class_label+'11454657142157-Shoetopia-Women-Casual-Shoes-9861454657141630-1_mini.jpg.txt')
# init = init1
# for i in [init2,init3,init4,init5]:
#     init = np.append(init, i, axis=0)
# print((init))




path = path_dest + bneck
# features = joblib.load(path+'tshirts/0/features.pkl')
# image_names = joblib.load(path+'tshirts/0/image_names.pkl')
# print(len(features), len(image_names))
# print(features[0],image_names[0])
#
for i in class_label:
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
            if len(features) == 0:
                features = np.array(build_data_frame(p + fn))
                image_names.append(image)
            else:
                try:
                    dataset = build_data_frame(p + fn)
                    features = np.append(features, dataset, axis=0)
                    image_names.append(image)
                except:
                    pass
        joblib.dump(features, p + 'features.pkl')
        joblib.dump(image_names, p + 'image_names.pkl')
# print(features)
# for K in range(2, 8, 1):
#     t = time()
#     if K ==5:
#         km = KMeans(n_clusters=K, init=init, max_iter=100, n_init=1)
#     else:
#         km = KMeans(n_clusters=K, init='k-means++', max_iter=100, n_init=1)
#     km.fit(features)
#     st = time()
#     centroids = km.cluster_centers_
#     labels = km.labels_
#     print("For K=" + str(K) + "time=" + str(st-t))
#     print(silhouette_score(features, labels, metric='euclidean'))

# km = KMeans(n_clusters=2, init=init, max_iter=10, n_init=1)
# km.fit(features)
# centroids = km.cluster_centers_
# labels = km.labels_
# print(silhouette_score(features, labels, metric='euclidean'))
#
# # f = open(path_dest + bneck + class_label + 'centroids.csv', 'w+')
# # for i in centroids:
# #     for j in i:
# #         f.write(str(j) + ',')
# #     f.write("\n")
# # f.close()
#
# cnt = -1
#
# for fn in os.listdir(path_bn + class_label):
#     cnt += 1
#     i = os.path.splitext(fn)[0]
#     try:
#         shutil.copy2(path_img + class_label + i, path_dest + str(labels[cnt]))
#     except OSError:
#         pass
#     # try:
#     #     shutil.copy2(path_bn + class_label + fn, path_dest + bneck + class_label + str(labels[cnt]))
#     # except OSError:
#     #     pass
