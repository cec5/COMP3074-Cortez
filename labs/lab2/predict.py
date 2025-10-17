import os
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from joblib import load

new_data = input('Enter a review/statement that is either positive or negative:\n')
new_data = [new_data]

classifier = load('joblib/classifier.joblib')
count_vect = load('joblib/count_vect.joblib')
tfidf_transformer = load('joblib/tfidf_transformer.joblib')

processed_new_data = count_vect.transform(new_data)
processed_new_data = tfidf_transformer.transform(processed_new_data)

print("Your statement is: "+str(classifier.predict(processed_new_data)))