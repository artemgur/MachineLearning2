from cluster import clusterDBSCAN
from vectorize import vectorize
import streamlit as st


class Hyperparameters:
    def __init__(self, ngram_min, ngram_max, max_features, eps, min_samples, vocabulary):
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.max_features = max_features
        self.eps = eps
        self.min_samples = min_samples
        self.vocabulary = vocabulary
        self.suspicious_strings = None



@st.experimental_memo
def vectorize_cluster(data, ngram_min, ngram_max, max_features, eps, min_samples, vocabulary=None):
    vectorized_tuple = vectorize(data, ngram_range=(ngram_min, ngram_max), max_features=max_features, vocabulary=vocabulary)
    vectorized = vectorized_tuple[0]
    clustered, clustered_vectorized = clusterDBSCAN(data, vectorized, eps=eps, min_samples=min_samples)
    duplicate_columns_removed = clustered_vectorized.loc[:, ~clustered_vectorized.columns.duplicated()]
    return clustered, duplicate_columns_removed, Hyperparameters(ngram_min, ngram_max, max_features, eps, min_samples, vectorized_tuple[1])
