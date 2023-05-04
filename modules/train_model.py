"""
Training model for detect DGA domains using machine learning
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
import numpy as np
import pickle
import time


def train(progress_queue):
    progress_queue.put((10, "Loading training dataset from disk..."))
    time.sleep(1)
    with open('input data/training_data.pkl', 'rb') as f:
        training_data = pickle.load(f)

    # Overall training data.
    all_data_dict = pd.concat([training_data['legit'], training_data['dga']], ignore_index=True)

    progress_queue.put((30, "Calculating length for each domain"))
    time.sleep(1)
    # Domains of any type (legit, dga) with length <6 receive very close results in the rating.
    # Also usually DGA domains have length > 6.
    # Based on this, they will not be taken into account in the model.
    all_data_dict['length'] = [len(x) for x in all_data_dict['domain']]
    all_data_dict = all_data_dict[all_data_dict['length'] > 6]

    progress_queue.put((60, "Creating model to definite matrix of ngram counts..."))
    time.sleep(1)
    # Min frequency = 0.001% for domains in overall data.
    # Remark: for 0.01% appears a lot zero values on occurrence ngram.
    vectorizer = CountVectorizer(ngram_range=(3, 5), analyzer='char', max_df=1.0, min_df=0.0001)

    progress_queue.put((80, "Counting the ngram occurrences of legit domains..."))
    # Result of sparse matrix (most of the entries are zero).
    # "(x,y) n" mean that "(row, column) value".
    # Value - the number of times a ngram appeared in the domains
    # represented by the row of the matrix.
    ngram_matrix = vectorizer.fit_transform(training_data['legit']['domain'])

    # Transform to dense matrix (column sum),
    # then to multidimensional homogeneous array.
    ngram_counts = ngram_matrix.sum(axis=0).getA1()

    # Relation extracted ngram out of raw domains in out sparse transpose matrix
    # with ngram_counts through multiplication of vectors.
    all_data_dict['occur_ngrams'] = ngram_counts * vectorizer.transform(all_data_dict['domain']).transpose()

    # Array x holdings the training samples.
    # Array y holdings the target values (type labels) for the training samples.
    X = all_data_dict[['length', 'occur_ngrams']].values
    y = np.array(all_data_dict['type'].tolist())

    # For the test, 20% of the original data is allocated.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    progress_queue.put((90, "Training model..."))
    # Fit a model.
    clf = RandomForestClassifier(n_estimators=10)
    clf = clf.fit(X_train, y_train)

    progress_queue.put((100, "Saving model to disk"))
    time.sleep(1)
    joblib.dump(clf, 'input data/model.pkl')


if __name__ == "__main__":
    train()
