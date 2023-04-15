import sys
import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import NMF


# - - - - - - - - - - - - - - - - - - - -
def print_top_words(model, feature_names, n_top_words=7):
    for topic_idx, topic in enumerate(model.components_):
        message = "Тема %d: " % topic_idx
        message += " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)


# - - - - - - - - - - - - - - - - - - - -
def main():
    n_features = 1000
    n_components = 10

    df = pd.read_pickle('data/rss-all_pandas.pkl')
    print('текстов:', len(df))

    data = df['text'].tolist()

    with open('data/stop-words-russian.txt', 'r') as f:
        stop_words_russian = f.read()
    stop_words_russian = stop_words_russian.split()
    print('количество стоп-слов:', len(stop_words_russian))

    data = [re.sub(r'\b\d+\b', ' ', t.lower()) for t in data]  # удаление цифр

    # tf features
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words=stop_words_russian)
    tf = tf_vectorizer.fit_transform(data)
    tf_feature_names = tf_vectorizer.get_feature_names()

    # LDA - латентное размещение Дирихле
    lda = LatentDirichletAllocation(n_components=n_components, max_iter=5, learning_method='online',
                                    learning_offset=50., random_state=0).fit(tf)
    print('\nLDA:\n')
    print_top_words(lda, tf_feature_names)

    # tf-idf features
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words=stop_words_russian)
    tfidf = tfidf_vectorizer.fit_transform(data)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    # NMF (Frobenius norm) - неотрицательное матричное разложение
    nmf = NMF(n_components=n_components, random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf)
    print('\nNMF(Frobenius norm):\n')
    print_top_words(nmf, tfidf_feature_names)

    # NMF (generalized Kullback-Leibler divergence)
    nmf = NMF(n_components=n_components, random_state=1, beta_loss='kullback-leibler', solver='mu', max_iter=1000,
              alpha=.1, l1_ratio=.5).fit(tfidf)
    print('\nNMF(generalized Kullback-Leibler divergence):\n')
    print_top_words(nmf, tfidf_feature_names)


# - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
    sys.exit(main())