import pandas as pd  # импортирование библиотеки pandas и задание краткого имени pd
import re  # импортирование библиотеки re (Regular Expression) для работы с регулярными выражениями
import nltk  # импортирование библиотеки nltk (Natural Language Toolkit) для работы с естественным языком
from sklearn.feature_extraction.text import \
    CountVectorizer  # импортирование класса CountVectorizer для извлечения признаков из текстов
from sklearn.model_selection import train_test_split, \
    GridSearchCV  # импортирование функций для разбиения на обучающую и тестовую выборки, а также для подбора гиперпараметров с помощью кросс-валидации
from sklearn.pipeline import Pipeline  # импортирование класса Pipeline для создания цепочек преобразований и моделей
from sklearn.metrics import accuracy_score  # импортирование метрики accuracy_score для оценки качества классификации
from sklearn.naive_bayes import \
    MultinomialNB  # импортирование класса MultinomialNB для построения наивного байесовского классификатора
import joblib  # импортирование модуля joblib для сохранения модели в файл

# Загрузка данных
data = pd.read_csv(
    'train_data.csv')  # чтение данных из csv-файла и создание DataFrame с помощью метода read_csv из pandas

# Предобработка текстов
data['text'] = data['text'].fillna('').apply(lambda x: re.sub(r'[^a-zA-Zа-яА-Я]', ' ',
                                                              x))  # заполнение пропущенных значений в столбце text пустой строкой, затем удаление всех символов, кроме букв русского и английского алфавитов

# Разделение на признаки и целевую переменную
X = data['text']  # выбор столбца text в качестве признаков
y = data['tag']  # выбор столбца tag в качестве целевой переменной

# Разбиение на тренировочную и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                    random_state=42)  # разбиение данных на обучающую и тестовую выборки в соотношении 80/20

# Создание пайплайна
pipeline = Pipeline([  # создание последовательности преобразований и модели в Pipeline
    ('vect', CountVectorizer(stop_words=nltk.corpus.stopwords.words('russian'))),
    # извлечение признаков из текстов с помощью CountVectorizer, исключая стоп-слова русского языка из библиотеки NLTK
    ('clf', MultinomialNB())  # модель классификации текстов на основе наивного Байеса с мультиномиальным распределением
])

# Подбор гиперпараметров
parameters = {  # задание сетки гиперпараметров для перебора
    'vect__ngram_range': [(1, 1), (1, 2)],  # выбор диапазона n-грамм, которые будут извлекаться
    'vect__max_df': [0.5, 0.75, 1.0],
    # выбор максимальной доли документов, в которых слово может появляться, чтобы оно было включено в словарь
    'clf__alpha': [0.1, 0.5, 1.0]  # выбор коэффициента сглаживания для модели наивного Байеса
}
grid_search = GridSearchCV(pipeline, parameters, cv=5,
                           n_jobs=-1)  # перебор гиперпараметров с помощью GridSearchCV и кросс-валидацией на 5 фолдах

grid_search.fit(X_train, y_train)  # обучение модели на тренировочной выборке с использованием перебора гиперпараметров

# Оценка качества модели на тестовой выборке
y_pred = grid_search.predict(X_test)  # получение предсказаний на тестовой выборке
accuracy = accuracy_score(y_test, y_pred)  # вычисление точности модели на тестовой выборке
print('Accuracy on test set: {:.2f}'.format(accuracy))  # вывод точности модели на тестовой выборке

joblib.dump(grid_search.best_estimator_, 'text_model.pkl')  # сохранение лучшей модели в файл
print('Best parameters: {}'.format(grid_search.best_params_))  # вывод лучших гиперпараметров, найденных при переборе
