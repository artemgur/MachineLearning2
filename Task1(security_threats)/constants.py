# IO
#default_data_url = 'https://docs.google.com/spreadsheets/d/1Y9Z-i5YGQob5r5tR8fF-UQNXH8waDGexeVBKz0XOGTk/export?format=csv&id=1Y9Z-i5YGQob5r5tR8fF-UQNXH8waDGexeVBKz0XOGTk&gid=920650402'
default_data_url = 'https://docs.google.com/spreadsheets/d/1laSpq2WiDuOwxYlm-jGg2Xpix3bgd5cryEpNI6XnSbw/export?format=csv&id=1laSpq2WiDuOwxYlm-jGg2Xpix3bgd5cryEpNI6XnSbw&gid=72133023'
suspicious_strings_file_path = 'SuspiciousStrings.txt'

# Preprocessing
supported_initial_columns = ['meta1', 'meta2', 'meta3', 'vector']
drop_nan_threshold = 0.1

# Vectorization hyperparameters
ngram_lower = 3
ngram_upper = 3
max_features = 1000

# Clustering hyperparameters
eps = 1.9
min_samples = 15

# Catboost cat_features
cat_features = ['meta1', 'meta2', 'meta3', 'http_code_type']

# Train only on a subset
train_on_subset = True
train_subset_size = 100

# Model saving
default_model_filename = 'catboost_model.cbm'
default_target_filename = 'catboost_predicted.csv'
hyperparameters_suffix = "_Hyperparameters.txt"
