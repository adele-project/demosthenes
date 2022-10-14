import json
import os
import re
import string

import numpy as np
import pandas as pd
from nltk.corpus import stopwords


def remove_stopwords(text, language):
    stpword = stopwords.words(language)
    no_punctuation = [char for char in text if char not in string.punctuation]
    no_punctuation = ''.join(no_punctuation)
    return ' '.join([word for word in no_punctuation.split() if word.lower() not in stpword])


def uniform(el):
    # sorted list of values for multi-value attributes
    if el == el:
        if '|' in el:
            el = sorted(el.split('|'))
        elif isinstance(el, list):
            el = sorted(el)
    return el


def create_df_annotations(path, crossvalfolds={}):
    temp = []

    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r', encoding='utf8') as f:
            data = json.load(f)
            annotations = data["annotations"]

            split = int(crossvalfolds[filename.split('_')[1].split('.')[0]])

            for annotation in annotations:
                if annotation["name"] != 'conc' and annotation["name"] != 'prem':
                    continue
                document = data["document"]["name"]
                name = annotation["name"]
                _id = annotation["_id"]
                text = data["document"]["plainText"][int(annotation["start"]):int(annotation["end"])]
                # attribute extraction, NaN if that attribute is not present
                T = uniform(annotation["attributes"].get("T", np.nan))
                S = uniform(annotation["attributes"].get("S", np.nan))

                text = clean(text, 'english')
                text = text.lstrip('‘’\'\n0123456789.-–…;;) ')
                text = text.rstrip('‘’\'\n.;; ')

                temp.append([document, split, name, _id, text, T, S])

    # df creation
    df = pd.DataFrame(temp,
                      columns=['Document', 'Split', 'Name', 'Id', 'Text', 'Type', 'Scheme'])

    # remove stopwords and punctuation from each sentence
    df["Text"] = df["Text"].apply(lambda x: remove_stopwords(x, 'english'))

    df.to_pickle("./df_annotations.pkl")


def clean(text, language):
    # deletes ...
    text = re.sub(r'\.\.\.', ' ', text)
    # deletes . from paragraphs' numbers: 2.1 -> 21
    text = re.sub(r'(\d+)\.(\d+)', r'\1\2', text)
    # same if number is 1.2.3.
    text = re.sub(r'(\d+)\.(\d+)\.?', r'\1\2', text)
    # delete . from one-letter words: p., n., A.B.C., ...
    text = re.sub(r'(\w)\.(\w)\.(\w)\.(\w)\.', r'\1\2\3\4', text)
    text = re.sub(r'(\w)\.(\w)\.(\w)\.', r'\1\2\3', text)
    text = re.sub(r'(\w)\.(\w)\.', r'\1\2', text)
    text = re.sub(r'(\W)(\w)\.', r'\1\2', text)
    # some specific abbreviations
    text = re.sub(r'(\W)No\.', r'\1No', text)
    text = re.sub(r'(\W)Dr\.', r'\1Dr', text)
    text = re.sub(r'(\W)seq\.', r'\1seq', text)
    text = text.replace('andamp;', '')
    # delete ; between parenthesis
    for _ in range(0, 6):
        text = re.sub(r'\(([^\)]*);(.*)\)', r'(\1\2)', text)
    # delete \n between : and citation
    text = re.sub(r':(\n)+“(\d)*(\s)*', r': “', text, re.MULTILINE)
    text = re.sub(r':(\n)+‘(\d)*(\s)*', r': ‘', text, re.MULTILINE)

    return text


def create_df_all_sentences(path, crossvalfolds={}):
    temp = []

    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r', encoding='utf8') as f:
            data = json.load(f)
            plainText = data["document"]["plainText"]

            # text cleaning
            plainText = clean(plainText, 'english')

            sentences = re.split('[.;\n]', plainText)  # split text at every . or ; or newline

            # cleaning again
            sentences = [item.lstrip('‘’\'\n\t0123456789.-–…;) ') for item in sentences]
            sentences = [item.rstrip('‘’\'\n\t.; ') for item in sentences]
            # remove empty strings and very short strings
            sentences = [item for item in sentences if item]
            sentences = [item for item in sentences if len(item) > 5]

            split = int(crossvalfolds[filename.split('_')[1].split('.')[0]])

            annotations = data["annotations"]
            for annotation in annotations:
                if annotation["name"] != 'conc' and annotation["name"] != 'prem':
                    continue

                document = annotation["document"]
                name = annotation["name"]
                # take the annotation from the unmodified text because 'start' and 'end' refer to that
                text = data["document"]["plainText"][int(annotation["start"]):int(annotation["end"])]
                # text cleaning to match the one in sentences
                text = clean(text, 'english')
                text = text.lstrip('‘’\'\n\t0123456789.-–…;) ')
                text = text.rstrip('‘’\'\n\t.; ')

                # if annotation in sentences: remove from the sentences list
                if text in sentences:
                    sentences.remove(text)
                    temp.append([document, split, name, text])

            # sentences still in the list aren't prem nor conc and they are appended with 'void' label
            for sentence in sentences:
                temp.append([document, split, 'void', sentence])

    # df creation
    df = pd.DataFrame(temp, columns=['Document', 'Split', 'Name', 'Text'])
    # remove stopwords and punctuation from each sentence
    df["Text"] = df["Text"].apply(lambda x: remove_stopwords(x, 'english'))

    df.to_pickle("./df_sentences.pkl")


# dataframes creation
crossvalfolds = {'1000': '1', '1001': '1', '1002': '1', '1003': '2', '1004': '2', '1005': '2', '1006': '3', '1007': '3', '1008': '3', '1009': '4', '1010': '4', '1011': '4', '1012': '5', '1013': '5', '1014': '5', '1015': '3',
                 '1016': '1', '1017': '1', '1018': '1', '1019': '1', '1020': '1', '1021': '2', '1022': '2', '1023': '2', '1024': '2', '1025': '5', '1026': '5', '1027': '3', '1028': '3', '1029': '3', '1030': '4', '1031': '4', '1032': '4', '1033': '4', '1034': '4', '1035': '2', '1036': '3', '1037': '5', '1038': '5', '1039': '5'}
create_df_annotations('.\\demosthenes_dataset_json', crossvalfolds=crossvalfolds)
create_df_all_sentences('.\\demosthenes_dataset_json', crossvalfolds=crossvalfolds)
