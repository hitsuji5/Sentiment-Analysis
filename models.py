from flask_sqlalchemy import SQLAlchemy
# import datetime
db = SQLAlchemy()

class Review(db.Model):
  __tablename__ = 'reviews'
  id = db.Column(db.Integer, primary_key = True)
  review = db.Column(db.String(200))
  sentiment = db.Column(db.Integer)
  # date = db.Column(db.DateTime, onupdate=datetime.datetime.now)

  def __init__(self, review, sentiment):
    self.review = review
    self.sentiment = sentiment
     
  # def set_password(self, password):
  #   self.pwdhash = generate_password_hash(password)
  #
  # def check_password(self, password):
  #   return check_password_hash(self.pwdhash, password)
