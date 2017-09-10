from PIL import Image


def get_main_color(file):
    img = Image.open(file)
    img = img.convert('RGB')
    colors = img.getcolors(2560000) #put a higher value if there are many colors in your image
    max_occurence, most_present = 0, 0
    for c in colors:
        if c[0] > max_occurence:
            (max_occurence, most_present) = c
    return most_present

# from sklearn.cluster import KMeans
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
#
# img = cv2.imread('red_shirt.jpg')
# height, width, dim = img.shape
# img = img[(height/4):(3*height/4), (width/4):(3*width/4), :]
# height, width, dim = img.shape
#
# img_vec = np.reshape(img, [height * width, dim] )
#
# kmeans = KMeans(n_clusters=3)
# kmeans.fit( img_vec )
# unique_l, counts_l = np.unique(kmeans.labels_, return_counts=True)
# sort_ix = np.argsort(counts_l)
# sort_ix = sort_ix[::-1]
#
# fig = plt.figure()
# ax = fig.add_subplot(111)
# x_from = 0.05
#
# for cluster_center in kmeans.cluster_centers_[sort_ix]:
#     ax.add_patch(patches.Rectangle( (x_from, 0.05), 0.29, 0.9, alpha=None,
#                                     facecolor='#%02x%02x%02x' % (cluster_center[2], cluster_center[1], cluster_center[0] ) ) )
#     x_from = x_from + 0.31
# plt.show()
