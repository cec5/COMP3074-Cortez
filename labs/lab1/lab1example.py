import nltk
import numpy as np
import scipy

#nltk.download('stopwords')
from urllib import request
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy import spatial

doc_urls = {
    "Russia":"http://www.gutenberg.org/cache/epub/13437/pg13437.txt",
    "France":"http://www.gutenberg.org/cache/epub/10577/pg10577.txt",
    "England":"http://www.gutenberg.org/cache/epub/10135/pg10135.txt",
    "USA":"http://www.gutenberg.org/cache/epub/10947/pg10947.txt",
    "Spain":"http://www.gutenberg.org/cache/epub/9987/pg9987.txt",
    "Scandinavia":"http://www.gutenberg.org/cache/epub/5336/pg5336.txt",
    "Iceland":"http://www.gutenberg.org/cache/epub/5603/pg5603.txt"
}

documents = {}
doc_ids = []

for country in doc_urls.keys():
    content = request.urlopen(doc_urls[country]).read().decode('utf8', errors='ignore')
    documents[country] =  content
    doc_ids.append(country)

all_text = documents.values()

count_vect = CountVectorizer(stop_words=stopwords.words('english'))
X_train_counts = count_vect.fit_transform(all_text)
tf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True).fit(X_train_counts)
X_train_tf = tf_transformer.fit_transform(X_train_counts)
#print(X_train_tf.shape)

stop = False
while not stop:
    query = input("Enter your search query, or STOP to quit, and press return: ")

    if query == "STOP":
        stop = True
    else:
        query_counts = count_vect.transform([query])
        query_tf = tf_transformer.transform(query_counts)
        query_vector = query_tf.toarray()[0]

        scores = []
        
        if np.linalg.norm(query_vector) == 0:
            print("\nQuery contains no words from the vocabulary\n")
            scores = [(doc_id, 0.0) for doc_id in doc_ids]
            continue
        else:
            for i in range(X_train_tf.shape[0]):
                doc_vector = X_train_tf.getrow(i).toarray()[0]
                if np.linalg.norm(doc_vector) == 0:
                    score = 0.0
                else:
                    score = 1 - spatial.distance.cosine(doc_vector, query_vector)
                
                scores.append((doc_ids[i], score))
        scores.sort(key=lambda x: x[1], reverse=True)
        
        print(f'\nYou are searching for "{query}"')
        print("--- Top 5 Results ---")
        for i, (doc_id, score) in enumerate(scores[:5]):
            print(f"Rank {i+1}: Document ID: {doc_id} with Score: {score:.4f}")
        print("-" * 20)
