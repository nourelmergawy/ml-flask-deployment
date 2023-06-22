#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pymongo
import pandas as pd
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
import random

app = Flask(__name__)


@app.route('/')
def home():
    return 'Server works'

@app.route('/test', methods=['POST'])
def test(): 
    userid = request.form.get('userid')
    return
@app.route('/recommendations/<userid>', methods=['POST'])
def recommendations(userid):
    # Specify the database URL and credentials
    url = "mongodb+srv://maryam:recobooks@cluster0.fhsy9vt.mongodb.net/?retryWrites=true&w=majority"

    # Create a client object
    client = pymongo.MongoClient(url)

    # Select the database and collection
    db = client['book']
    collection = db['users']
    # Retrieve data from the collection 
    #request.form.post('userid')
    userid = ObjectId(userid)
    user = collection.find_one({'_id': userid})
    # Convert the list of dictionaries to a Pandas DataFrame
    df_user = pd.DataFrame(user)
    books_list_mongo = df_user['favorits']
    books_list = pd.DataFrame(columns=['user_id','book_id', 'rating','title'])
    # Select the database and collection
    db = client['book']
    collection = db['books']
    for item in books_list_mongo :
        book_title = collection.find_one({'_id': ObjectId(item['_id'])})
        new_data = {'user_id':userid,'book_id': item['_id'], 'rating': item['rating'],'title':book_title['title']}
        books_list.loc[len(books_list)] = new_data
    books_set = set(books_list['book_id'].values.flatten())
    # Select the database and collection
    db = client['book']
    collection = db['users']
    user = collection.find({},{'_id':1,'favorits':1})
    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(user)


    overlap_users = {}
    for index, row in df.iterrows():
        for item in row :
            if type(item) != list:
                continue
            else :
                for book in item :
                    if book['_id'] in books_set:
                        if row['_id'] not in overlap_users:
                            overlap_users[row['_id']] = 1
                        else:
                            overlap_users[row['_id']] += 1

    filtered_overlap_users = set([k for k in overlap_users if overlap_users[k] > books_list.shape[0]/5])

    interactions_list = []
    for index, row in df.iterrows():
        for item in row :
            if type(item) != list:
                continue
            else :
                 for book in item :
                    if row['_id'] in filtered_overlap_users:
                        interactions_list.append([row['_id'], book['_id'], book['rating']])

    interactions = pd.DataFrame(interactions_list, columns=["user_id", "book_id", "rating"])
    interactions = pd.concat([books_list[["user_id", "book_id", "rating"]], interactions])
    interactions["book_id"] = interactions["book_id"].astype(str)
    interactions["user_id"] = interactions["user_id"].astype(str)
    interactions["rating"] = pd.to_numeric(interactions["rating"])
    interactions["user_index"] = interactions["user_id"].astype("category").cat.codes
    interactions["book_index"] = interactions["book_id"].astype("category").cat.codes
    from scipy.sparse import coo_matrix

    ratings_mat_coo = coo_matrix((interactions["rating"], (interactions["user_index"], interactions["book_index"])))
    ratings_mat = ratings_mat_coo.tocsr()
    interactions[interactions["user_id"] == str(userid)]
    my_index = 0
    from sklearn

    similarity = cosine_similarity(ratings_mat[my_index,:], ratings_mat).flatten()
    import numpy as np

    indices = np.argpartition(similarity, len(similarity)-1)[-len(similarity):]
    similar_users = interactions[interactions["user_index"].isin(indices)].copy()
    similar_users = similar_users[similar_users["user_id"]!=str(userid)]
    books_titles = pd.read_csv("C:/Users/mergo/Desktop/books.csv")
    # Assuming 'df' is your DataFrame
    columns_to_drop = ["Unnamed: 0","book_id"]
    books_titles = books_titles.drop(columns_to_drop, axis=1)
    # Assuming 'df' is your DataFrame
    books_titles.rename(columns={'_id': 'book_id'}, inplace=True)
    book_recs = similar_users.groupby("book_id").rating.agg(['count', 'mean'])
    book_recs = book_recs.merge(books_titles, how="inner", on="book_id")
    book_recs["adjusted_count"] = book_recs["count"] * (book_recs["count"] / book_recs["ratings"])
    book_recs["score"] = book_recs["mean"] * book_recs["adjusted_count"]
    book_recs = book_recs[book_recs["mean"] >=4]
    
    return book_recs.to_json()


@app.route('/itembased/<userid>/<book_title>', methods=['POST'])
def itembased(userid, book_title):
    books_titles = pd.read_csv("C:/Users/mergo/Desktop/book_conc.csv")
    interactions = pd.read_csv("C:/Users/mergo/Desktop/final_interaction_conc.csv")
    interactions = interactions[['book_id', 'user_id', 'rating', 'title', 'ratings_count']]

    users_books_df = interactions.pivot_table(index='user_id', columns='title', values='rating')

    # Specify the database URL and credentials
    url = "mongodb+srv://maryam:recobooks@cluster0.fhsy9vt.mongodb.net/?retryWrites=true&w=majority"

    # Create a client object
    client = pymongo.MongoClient(url)

    # Select the database and collection
    db = client['book']
    collection = db['users']
    # Retrieve data from the collection
    # request.form.post('userid')
    user_id = ObjectId(userid)
    user = collection.find_one({'_id': user_id})
    # Convert the list of dictionaries to a Pandas DataFrame
    df_user = pd.DataFrame(user)
    books_list_mongo = df_user['favorits']

    books_list = pd.DataFrame(columns=['user_id', 'book_id', 'rating', 'title', 'ratings_count'])

    # Select the database and collection
    db = client['book']
    collection = db['books']
    for item in books_list_mongo:
        book_title = collection.find_one({'_id': ObjectId(item['_id'])})
    if book_title['ratings_count'] != None:
        new_data = {'user_id': userid, 'book_id': item['_id'], 'rating': item['rating'], 'title': book_title['title'],
                    'ratings_count': book_title['ratings_count']}
        books_list.loc[len(books_list)] = new_data

    books_given_5_points = books_list[books_list['rating'] == 5]
    item_based_5_books = users_books_df.corrwith(users_books_df[book_title])
    item_based_5_books = item_based_5_books.to_frame()
    item_based_5_books = item_based_5_books[:20]
    final_list = books_titles.merge(item_based_5_books, how="inner", on="title")
    book_recs_list = []
    for index, row in final_list.iterrows():
        book_rec_dict = {
            "book_id": row["_id"],
            "title": row["title"],
            "ratings": row["ratings"],
            "url": row["url"],
            "description": row["description"],
            "publication_year": row["publication_year"],
            "cover_image": row["cover_image"],
            "country_code": row["country_code"],
            "publisher": row["publisher"]
        }
    book_recs_list.append(book_rec_dict)
    return jsonify(results=book_recs_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)





