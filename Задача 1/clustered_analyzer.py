import pandas as pd
import matplotlib.pyplot as plt


def column_hist(streamlit_context, column):
    fig = plt.figure(figsize=(10, 4))
    plt.hist(column)
    streamlit_context.pyplot(fig)


def hist_clusters_of_column_values(streamlit_context, clustered, column_name, value):
    column_hist(streamlit_context, clustered[clustered[column_name] == int(value)]['clustering_result']) # TODO fix int cast


def get_clustering_stats(clustered):
    rows_count = clustered.shape[0]
    unclassified_count = clustered[clustered['clustering_result'] == -1].shape[0]
    unclassified_ratio = unclassified_count / rows_count
    cluster_count = clustered['clustering_result'].nunique()
    return unclassified_count, unclassified_ratio, cluster_count

#def cluster_distribution_hist(streamlit_context, clustered):
#    a = clustered.groupby(['clustering_result']).size().to_frame('size').reset_index().set_index('clustering_result')
#    column_hist(streamlit_context, a)
