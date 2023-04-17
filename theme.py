import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Чтение обучающего набора данных из CSV-файла
train_data = pd.read_csv('train.csv', delimiter=';', header=0)

# Предобработка текстов
train_data['text'] = train_data['text'].str.lower()  # приведение к нижнему регистру

# Преобразование текстов в числовые векторы
vectorizer = TfidfVectorizer(stop_words='english')
X_train = vectorizer.fit_transform(train_data['text'])

# Обучение модели на обучающем наборе данных
clf = MultinomialNB()
clf.fit(X_train, train_data['tag'])

# Чтение тестового набора данных из CSV-файла
test_data = pd.read_csv('test.csv', delimiter=';', header=0)

# Предобработка текстов
test_data['text'] = test_data['text'].str.lower()  # приведение к нижнему регистру

# Преобразование текстов в числовые векторы
X_test = vectorizer.transform(test_data['text'])

# Классификация тестовых текстов с помощью обученной модели
y_pred = clf.predict(X_test)

# Оценка точности модели на тестовом наборе данных
accuracy = accuracy_score(test_data['tag'], y_pred)
print(f'Accuracy: {accuracy:.2f}')

results = {}
for i in range(len(test_data)):
    results[test_data['text'][i]] = y_pred[i]

# Вывод результатов
for text, tag in results.items():
    print(f'{text} : {tag}')