from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
import os
import json
from models import db, Review
from classifier import clf
from tweepy import OAuthHandler
from tweepy import API


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/nlp'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

# print clf.predict(['This was a sad movie I have seen',
#          'Great! I love that.'])

######## Setup Twitter API
#Variables that contains the user credentials to access Twitter API
cur_dir = os.path.dirname(__file__)
with open(os.path.join(cur_dir, 'twitter_api.json'), 'r') as f:
    api_keys = json.load(f)

access_token = api_keys['access_token']
access_token_secret = api_keys['access_token_secret']
consumer_key = api_keys['consumer_key']
consumer_secret = api_keys['consumer_secret']
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

######## Flask
class SearchForm(Form):
    word = TextAreaField('', [validators.DataRequired(), validators.length(min=3)])

@app.route('/')
def index():
    form = SearchForm(request.form)
    return render_template('reviewform.html', form=form)

@app.route('/results', methods=['POST'])
def results():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        word = request.form['word']
        try:
            results = api.search(q=word, lang='en')
            texts = [r.text for r in results]
            date = [r.created_at.strftime("%Y/%m/%d %H:%M:%S") for r in results]
            scores = clf.predict(texts)
            tweets = zip(date, texts, scores)
            tweets.sort(key=lambda x: x[2], reverse=True)
        except:
            print 'Error'
            tweets = []
        return render_template('results.html', word=word, tweets=tweets)
    return render_template('reviewform.html', form=form)

@app.route('/thanks', methods=['POST'])
def feedback():
    feedback = request.form['feedback_button']
    word = request.form['word']
    # prediction = request.form['prediction']
    # inv_label = {'negative': 0, 'positive': 1}
    # y = inv_label[prediction]
    y = 1 if feedback == 'Incorrect' else 0
    review = Review(word, y)
    db.session.add(review)
    db.session.commit()
    return render_template('thanks.html')

if __name__ == '__main__':
    app.run(debug=True)
