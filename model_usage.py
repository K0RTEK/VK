import joblib
text = input('Введите текст: ')
while text!='0':
    model = joblib.load('text_model.pkl')
    tag = model.predict([text])[0]
    print('Tag: {}'.format(tag))
    text = input('Введите текст: ')