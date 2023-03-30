import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def vectorize(data, ngram_range, max_features, vocabulary=None):
    string_series = data['vector']
    data_temp = data.drop('vector', axis=1)

    if max_features == 0:
        return data_temp

    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=ngram_range, max_features=max_features, vocabulary=vocabulary)
    string_series_vectorized = vectorizer.fit_transform(string_series)

    string_df_vectorized = pd.DataFrame(string_series_vectorized.toarray(), columns=vectorizer.get_feature_names_out(),
                                        index=data_temp.index)

    return pd.concat([data_temp, string_df_vectorized], axis=1), vectorizer.get_feature_names_out()
