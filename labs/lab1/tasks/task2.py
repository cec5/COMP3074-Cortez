import os
import nltk
import scipy
import pickle
import numpy as np

from nltk.corpus import stopwords;
from nltk.stem.snowball import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy import spatial

# Preprocessing
script_dir = os.path.dirname(os.path.abspath(__file__))
document_path = os.path.join(script_dir,"data")
corpus = {}
doc_ids = []
for file in os.listdir(document_path):
    filepath = document_path + os.sep + file
    with open(filepath, encoding='utf8', errors='ignore', mode='r') as document:
        content = document.read()
        document_id = file
        corpus[document_id] = content
        doc_ids.append(document_id)

p_stemmer = PorterStemmer()
def stemmed_words_analyzer():
    analyzer = CountVectorizer().build_analyzer()
    return lambda doc: (p_stemmer.stem(w) for w in analyzer(doc))

all_text = corpus.values()
count_vect = CountVectorizer(stop_words=stopwords.words('english'), analyzer=stemmed_words_analyzer())
X_train_counts = count_vect.fit_transform(all_text)
tf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
idf_values = tf_transformer.idf_

vocabulary_data = {}
for term, term_id in count_vect.vocabulary_.items():
    vocabulary_data[term] = {
        'term_id': term_id,
        'canonical_form': term,
        'idf' : idf_values[term_id]
    }

with open('vocabulary.pickle','wb') as f:
    pickle.dump(vocabulary_data,f)
with open('vocabulary.pickle','rb') as f:
    vocabulary_data = pickle.load(f)

# Query logic
stop = False
while not stop:
    query = input("Enter your query, or STOP to quit: ")
    if query == "STOP":
        stop = True
    else:
        print(f'You are searching for: {query}')
        query_counts = count_vect.transform([query])
        query_tf = tf_transformer.transform(query_counts)
        query_vector = query_tf.toarray()[0]

        scores = []
 
        if np.linalg.norm(query_vector) == 0:
            print("Query contains no words from the vocabulary")
            scores = [(doc_id, 0.0) for doc_id in doc_ids]
        else:
            for i in range(X_train_tf.shape[0]):
                doc_vector = X_train_tf.getrow(i).toarray()[0]
                if np.linalg.norm(doc_vector) == 0:
                    score = 0.0
                else:
                    score = 1 - spatial.distance.cosine(doc_vector, query_vector)
                scores.append((doc_ids[i], score))
        scores.sort(key=lambda x: x[1], reverse=True)

        print("\n--- Top 10 Results ---")
        for i, (doc_id, score) in enumerate(scores[:10]):
            print(f"Rank {i+1}: Document ID: {doc_id} | Score: {score:.4f}")
        print("-" * 25)
