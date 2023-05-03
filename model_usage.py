import joblib
from main import get_users_subscriptions_posts
from main import find_most_frequent_word

model = joblib.load('text_model.pkl')
data = get_users_subscriptions_posts()

for u_id, item in data.items():
    for g_id, arr in dict(item).items():
        for idx, text in enumerate(arr):
            data[u_id][g_id][idx] = model.predict([text])[0]
        data[u_id][g_id] = find_most_frequent_word(data[u_id][g_id])

print(data)
