import pandas as pd
import argumentmining

# read data
df_sentences = pd.read_pickle(".\\df_sentences.pkl")
df_annotations = pd.read_pickle(".\\df_annotations.pkl")

# list of classifiers and embeddings to try
classifiers = ['linearsvc', 'randomforest', 'gaussiannb', 'kneighbors', 'svc']
# classifiers = ['random', 'majority']
embeddings = ['tfidf', 'sbert', 'legalbert']

# argument detection
argumentmining.argument_classification(df_sentences, classifiers, embeddings)

# argument classification
argumentmining.argument_classification(df_annotations, classifiers, embeddings)

# type classification
argumentmining.attribute_classification(df_annotations, classifiers, embeddings, 'Type')

# scheme classification
argumentmining.attribute_classification(df_annotations, classifiers, embeddings, 'Scheme')
