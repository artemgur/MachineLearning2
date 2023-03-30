import pandas as pd
from sklearn.cluster import DBSCAN


def cluster(data, data_vectorized, clusterer):
    # Применим One-Hot кодирование к категориальным признакам.
    encoded = pd.get_dummies(data_vectorized)
    # Кластеризация
    clustering_result = clusterer.fit_predict(encoded.dropna())
    # Присоединение результатов векторизации к данным (не векторизованным)
    clustered_series = pd.DataFrame(clustering_result, columns=['clustering_result'], index=data_vectorized.index)

    return pd.concat([data, clustered_series], axis=1), pd.concat([data_vectorized, clustered_series], axis=1)


def clusterDBSCAN(data, vectorized, eps, min_samples):
    return cluster(data, vectorized, DBSCAN(eps=eps, min_samples=min_samples))
