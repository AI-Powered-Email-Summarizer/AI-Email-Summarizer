import pickle

# Load vectorizer & model
with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("spam_model.pkl", "rb") as f:
    model = pickle.load(f)

def is_spam(text):
    """Returns True if spam, False if not spam"""
    input_vectorized = vectorizer.transform([text])
    prediction = model.predict(input_vectorized)[0]
    return prediction == 1  # True for spam, False for not spam
