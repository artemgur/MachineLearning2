import constants as c
from sklearn.model_selection import train_test_split
import streamlit as st
#import catboost
from catboost import CatBoostClassifier, Pool
from sklearn.metrics import precision_score, recall_score, accuracy_score
import pandas as pd
import jsonpickle
import constants as const

def train_model(x_train, y_train, cat_features):
    pool_train = Pool(x_train, y_train, cat_features)
    cat = CatBoostClassifier(task_type="GPU")
    cat.fit(pool_train)
    return cat

def test_model(cat, x_test, y_test, cat_features):
    pool_test = Pool(x_test, cat_features=cat_features)
    pred = cat.predict(pool_test)
    return accuracy_score(y_test, pred), recall_score(y_test, pred, average='macro'), precision_score(y_test, pred, average='macro')

@st.experimental_memo
def train_test(data):
    train_subset = data.head(c.train_subset_size) if c.train_on_subset else data
    x_train, x_test, y_train, y_test = train_test_split(train_subset.drop('clustering_result', axis=1),
                                                        train_subset['clustering_result'], test_size=0.2)
    cat = train_model(x_train, y_train, c.cat_features)
    return cat, test_model(cat, x_test, y_test, c.cat_features)

def save_model(cat, file_name, vectorization_clustering_hyperparameters, suspicious_strings):
    cat.save_model(file_name + ".cbm", format='cbm')
    #shutil.copy("SuspiciousStrings.txt", file_name + "_SuspiciousStrings.txt")
    vectorization_clustering_hyperparameters.suspicious_strings = suspicious_strings
    json_string = jsonpickle.encode(vectorization_clustering_hyperparameters)
    with open(file_name + const.hyperparameters_suffix, 'w') as file:
        file.write(json_string)

def load_model(file_name):
    cat = CatBoostClassifier()
    return cat.load_model(file_name + ".cbm", format='cbm')

def predict(cat, data):
    return cat.predict(data)

def predict_by_filename(file_name, clustered_vectorized, original_data):
    cat = load_model(file_name)
    prediction_array = cat.predict(clustered_vectorized)
    prediction_series = pd.DataFrame(prediction_array, columns=['prediction'], index=original_data.index)
    return pd.concat([original_data, prediction_series], axis=1)


