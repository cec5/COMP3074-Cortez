import os
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from joblib import dump, load

# Import all data first (tf I didn't do it this way last week)
label_dir = {
    "positive":"data/positive",
    "negative":"data/negative"
}

data = []
labels = []

for label in label_dir.keys():
    for file in os.listdir(label_dir[label]):
        filepath = label_dir[label] + os.sep + file
        with open(filepath, encoding ='utf8', errors='ignore' ,mode='r') as review:
            content = review.read()
            data.append(content)
            labels.append(label)

X_train, X_test, y_train, y_test = train_test_split(data, labels, stratify = labels, test_size=0.25, random_state=42)

count_vect = CountVectorizer (stop_words = stopwords.words('english'))
X_train_counts = count_vect.fit_transform (X_train)

tfidf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True).fit(X_train_counts)
X_train_tf = tfidf_transformer.transform (X_train_counts)

classifier = LogisticRegression(random_state=0).fit(X_train_tf, y_train)

# Joblib 
dump(classifier, 'joblib/classifier.joblib')
dump(count_vect, 'joblib/count_vect.joblib')
dump(tfidf_transformer, 'joblib/tfidf_transformer.joblib')

X_new_counts = count_vect.transform(X_test)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)

predicted = classifier.predict(X_new_tfidf)

print(confusion_matrix(y_test, predicted))
print(accuracy_score(y_test, predicted))
print(f1_score(y_test, predicted, pos_label='positive'))