import random
import numpy as np
import pandas as pd
# from sklearn.cluster import KMeans


# 计算欧拉距离
def calcDis(dataSet, centroids, k):
    clalist=[]
    for data in dataSet:
        diff = np.tile(data, (k, 1)) - centroids  #相减   (np.tile(a,(2,1))就是把a先沿x轴复制1倍，即没有复制，仍然是 [0,1,2]。 再把结果沿y方向复制2倍得到array([[0,1,2],[0,1,2]]))
        squaredDiff = diff ** 2     #平方
        squaredDist = np.sum(squaredDiff, axis=1)   #和  (axis=1表示行)
        distance = squaredDist ** 0.5  #开根号
        clalist.append(distance) 
    clalist = np.array(clalist)  #返回一个每个点到质点的距离len(dateSet)*k的数组
    return clalist


# 计算质心
def classify(dataSet, centroids, k):
    # 计算样本到质心的距离
    clalist = calcDis(dataSet, centroids, k)
    # 分组并计算新的质心
    minDistIndices = np.argmin(clalist, axis=1)    #axis=1 表示求出每行的最小值的下标
    newCentroids = pd.DataFrame(dataSet).groupby(minDistIndices).mean() #DataFramte(dataSet)对DataSet分组，groupby(min)按照min进行统计分类，mean()对分类结果求均值
    newCentroids = newCentroids.values
 
    # 计算变化量
    changed = newCentroids - centroids
 
    return changed, newCentroids


# 使用k-means分类
def kmeans(dataSet, k):
    # 随机取质心
    centroids = random.sample(dataSet, k)
    
    # 更新质心 直到变化量全为0
    changed, newCentroids = classify(dataSet, centroids, k)
    while np.any(changed != 0):
        changed, newCentroids = classify(dataSet, newCentroids, k)
 
    centroids = sorted(newCentroids.tolist())   #tolist()将矩阵转换成列表 sorted()排序
 
    # 根据质心计算每个集群
    cluster = []
    clalist = calcDis(dataSet, centroids, k) #调用欧拉距离
    minDistIndices = np.argmin(clalist, axis=1)  
    for i in range(k):
        cluster.append([])
    for i, j in enumerate(minDistIndices):   #enymerate()可同时遍历索引和遍历元素
        cluster[j].append(dataSet[i])
        
    return centroids, cluster

def get_pt_center(input_array, n_clusters):
    centroids, cluster = kmeans(input_array.tolist(), n_clusters)
    
    return centroids, cluster

# def get_pt_center(input_array, n_clusters):
#     """聚类算法获取肿瘤靶向点
    
#     Args:
#         input_array: 肿瘤点集 -> 'numpy.ndarray'
#         n_clusters: 聚类簇数 -> 'int'

#     Return:
#         centers: 肿瘤靶向点坐标 -> 'numpy.ndarray'
#         predict: 肿瘤点集分类结果 -> 'numpy.ndarray'

#     Raises:
#         None
#     """
    
#     n_clusters = int(n_clusters)
#     kmeans = KMeans(n_clusters=n_clusters, n_init='auto')  # 获取模型
#     kmeans.fit(input_array)

#     centers = kmeans.cluster_centers_
#     # print(type(centers))
#     # print("center:", centers)
#     predict = kmeans.predict(input_array)
#     # print(type(predict))
#     # print(predict)

#     return centers, predict