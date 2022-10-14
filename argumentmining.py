import random

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC, SVC


def get_classifiers(names, multilabel=False):
    if 'random' in names or 'majority' in names:
        return names

    if multilabel:
        linear_classifier = OneVsRestClassifier(LinearSVC())
        rf_classifier = OneVsRestClassifier(RandomForestClassifier())
        nb_classifier = OneVsRestClassifier(GaussianNB())
        kn_classifier = OneVsRestClassifier(KNeighborsClassifier())
        svc_classifier = OneVsRestClassifier(SVC(kernel='poly'))
    else:
        linear_classifier = LinearSVC()
        rf_classifier = RandomForestClassifier()
        nb_classifier = GaussianNB()
        kn_classifier = KNeighborsClassifier()
        svc_classifier = SVC(kernel='poly')

    classifiers = []
    if 'linearsvc' in names:
        classifiers.append(linear_classifier)
    if 'randomforest' in names:
        classifiers.append(rf_classifier)
    if 'gaussiannb' in names:
        classifiers.append(nb_classifier)
    if 'kneighbors' in names:
        classifiers.append(kn_classifier)
    if 'svc' in names:
        classifiers.append(svc_classifier)
    return classifiers


def get_embeddings(corpus, embedding):  # embedding in [tfidf, sbert, legalbert]
    if embedding == "sbert":
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        sentence_embeddings = model.encode(corpus)
    elif embedding == "legalbert":
        model = SentenceTransformer("nlpaueb/legal-bert-small-uncased")
        sentence_embeddings = model.encode(corpus)
    elif embedding == "tfidf":
        vectorizer = TfidfVectorizer()
        sentence_embeddings = vectorizer.fit_transform(corpus)
        sentence_embeddings = sentence_embeddings.toarray()
        return sentence_embeddings
    else:
        print("wrong embedding name")
        return
    return sentence_embeddings


def argument_classification(df, classifiers, embeddings):
    corpus = df['Text'].values
    random.seed(42)
    for embedding in embeddings:
        X = get_embeddings(corpus, embedding)

        for classifier in get_classifiers(classifiers):
            y_pred_all = None
            y_test_all = None
            for fold in range(1, 6):
                X_train = X[df['Split'] != fold]
                X_test = X[df['Split'] == fold]

                y_train = df[df['Split'] != fold]['Name']
                y_test = df[df['Split'] == fold]['Name']

                if classifier == 'random':
                    labs = list(set(y_train))
                    y_pred = [random.choice(labs) for _ in range(len(X_test))]
                elif classifier == 'majority':
                    labs = set(y_train)
                    maj = 0
                    for l in labs:
                        val = list(y_train).count(l)
                        if val > maj:
                            majority_class = l
                            maj = val
                    y_pred = [majority_class for _ in range(len(X_test))]
                else:
                    classifier.fit(X_train, y_train)
                    y_pred = classifier.predict(X_test)

                y_pred_all = y_pred if y_pred_all is None else np.concatenate([y_pred_all, y_pred])
                y_test_all = y_test if y_test_all is None else np.concatenate([y_test_all, y_test])

            labels = sorted(set(y_train))

            report = classification_report(y_test_all, y_pred_all, target_names=labels)
            print(embedding + " " + str(classifier.__class__).split('.')[-1].split("'")[0])
            print(report)


def attribute_classification(df, classifiers, embeddings, attribute):
    df = df.dropna(subset=[attribute])
    df[attribute] = df[attribute].apply(lambda x: [x] if not isinstance(x, list) else x)

    df[attribute] = df[attribute].apply(lambda x: sorted(list(set(x))) if x != [] else np.NaN)
    df = df.dropna(subset=[attribute])

    print(df[attribute].value_counts())

    corpus = df['Text'].values

    for embedding in embeddings:
        X = get_embeddings(corpus, embedding)

        for classifier in get_classifiers(classifiers, multilabel=True):
            labels = set()
            y_pred_all = None
            y_test_all = None
            for fold in range(1, 6):
                X_train = X[df['Split'] != fold]
                X_test = X[df['Split'] == fold]

                y_train = df[df['Split'] != fold][attribute]
                y_test = df[df['Split'] == fold][attribute]

                ml = MultiLabelBinarizer()
                y_train = ml.fit_transform(y_train)
                y_test = ml.fit_transform(y_test)
                labels = labels.union(ml.classes_)

                if classifier == 'random':
                    y_pred = [random.sample(labels, random.randint(1, len(labels))) for _ in range(len(X_test))]
                    y_pred = ml.transform(y_pred)
                elif classifier == 'majority':
                    mask = []
                    for l in sorted(labels):
                        count = 0
                        for element in list(ml.inverse_transform(y_train)):
                            if l in element:
                                count += 1
                        if count > len(list(y_train))/2:
                            mask.append(True)
                        else:
                            mask.append(False)
                    sample = [1 if el else 0 for el in mask]
                    y_pred = [sample for _ in range(len(X_test))]
                else:
                    classifier.fit(X_train, y_train)
                    y_pred = classifier.predict(X_test)

                y_pred_all = y_pred if y_pred_all is None else np.concatenate([y_pred_all, y_pred])
                y_test_all = y_test if y_test_all is None else np.concatenate([y_test_all, y_test])

            labels = sorted(labels)

            report = classification_report(y_test_all, y_pred_all, target_names=labels)
            print(embedding + " " + str(classifier.__class__).split('.')[-1].split("'")[0])
            print(report)

