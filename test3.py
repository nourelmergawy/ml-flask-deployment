import pandas as pd
import pymongo
from bson.objectid import ObjectId
import numpy as np
import os
import re
import nltk
import requests
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bson.objectid import ObjectId
from nltk.corpus import stopwords
nltk.download("stopwords")



from PIL import Image
from flask import Flask, request

app = Flask(__name__)

# Specify the database URL and credentials
url = "mongodb+srv://maryam:recobooks@cluster0.fhsy9vt.mongodb.net/?retryWrites=true&w=majority"

# Create a client object
client = pymongo.MongoClient(url)

# Select the database and collection
db = client['book']
collection = db['usersact']
# Retrieve data from the collection
userid = ObjectId('64651cd380b60652c9fcfd88')
user = collection.find_one({'_id': userid})

# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(user)
favorits = df['favorits']
book_ids = [item['book_id'] for item in favorits]
# is_read_values = [item['is_read'] for item in favorits]
ratings = [item['rating'] for item in favorits]
mongo_book_id =[item['_id'] for item in favorits]
# print(mongo_book_id)
columns=['user_id','book_id', 'is_read', 'rating']
# print(my_books)
client.close()

#book collection
client_books = pymongo.MongoClient(url)
db_books = client_books['book']
collection_book = db_books['books']
mongo_book_title = []
print(mongo_book_id)
for data in mongo_book_id:
    books = collection_book.find_one({'_id': ObjectId(data)})
    mongo_book_title.append(books['title'])
my_books = pd.DataFrame({'user_id':userid,'book_id': book_ids, 'rating': ratings,'title':mongo_book_title})
print(my_books)
client.close()

# #interaction collection
# client_books = pymongo.MongoClient(url)
# db_books = client_books['book']
# collection_book = db_books['books']

interaction = pd.read_csv("1-2m-user-interaction.csv", index_col =0)
@app.route('/')
def home():
    return 'Server works'

@app.route('/recommendations', methods=['GET'])
def recommendations():

    return
if __name__ == "__main__":
    app.run()
