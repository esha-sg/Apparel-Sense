import operator
import os
import math

from sklearn.externals import joblib

path = "/home/eshwar/Downloads/tf_files/Apparel_Dataset/results/bottlenecks/"


def euclidean_distance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)


def get_similar_images(filename, label, bottleneck):
    lines = list(map(float, bottleneck))
    with open(path + label + '/centroids.csv', 'r') as f:
        ctr = 0
        l1 = {}
        for line in f:
            line = line[:-2]
            t = line.split(',')
            t = list(map(float, t))
            d = euclidean_distance(lines, t, len(t))
            l1[ctr] = d
            ctr += 1
    sorted_l1 = sorted(l1.items(), key=operator.itemgetter(1))
    cluster_label, v = sorted_l1[0]

    l2 = {}
    features = joblib.load(path + label + "/" + str(cluster_label) + "/features.pkl")
    image_names = joblib.load(path + label + "/" + str(cluster_label) + "/image_names.pkl")
    for i in range(len(features)):
        l = features[i]
        try:
            l = list(map(float, l))
            r2 = euclidean_distance(lines, l, len(l))
            l2[image_names[i]] = r2

        except ValueError:
            print("Error")

    sorted_l2 = sorted(l2.items(), key=operator.itemgetter(1))
    sorted_l2 = sorted_l2[0:10]
    h = []
    for i in range(0, 9):
        h.append(r'/static/data/' + label + '/' + str(cluster_label) + '/' + str(
            sorted_l2[i][0]))
    return h


def get_related_products(class_label, cluster_label, img_name):
    read_path = path + class_label + '/' + str(cluster_label) + '/'
    f = open(read_path + img_name)
    t = f.read().split(',')
    bottleneck = list(map(float, t))
    f.close()
    query_vector = list(map(float, bottleneck))
    l2 = {}
    features = joblib.load(read_path + 'features.pkl')
    image_names = joblib.load(read_path + 'image_names.pkl')
    for i in range(len(features)):
        l = features[i]
        try:
            l = list(map(float, l))
            r2 = euclidean_distance(query_vector, l, len(l))
            l2[image_names[i]] = r2

        except ValueError:
            print("Error")

    sorted_l2 = sorted(l2.items(), key=operator.itemgetter(1))
    sorted_l2 = sorted_l2[1:10]
    h = []
    for i in range(0, 9):
        h.append(r'/static/data/' + class_label + '/' + str(cluster_label) + '/' + str(sorted_l2[i][0]))
    return h
