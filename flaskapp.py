#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pymongo
import pandas as pd
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

books_titles = pd.read_csv("C:/Users/mergo/Desktop/50k_books.csv")
books_years_list = pd.read_csv("C:/Users/mergo/Desktop/years_df.csv")
books_popular = pd.read_csv("C:/Users/mergo/Desktop/40_most_popular_book.csv")
interactions = pd.read_csv("C:/Users/mergo/Desktop/final_interaction_conc.csv")
interactions = interactions[['book_id', 'user_id', 'rating', 'title', 'ratings_count']]
# users_books_df = pd.read_csv("C:/Users/mergo/Desktop/users_books_df.csv")
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
    from sklearn.metrics.pairwise import cosine_similarity

    similarity = cosine_similarity(ratings_mat[my_index,:], ratings_mat).flatten()
    import numpy as np

    indices = np.argpartition(similarity, len(similarity)-1)[-len(similarity):]
    similar_users = interactions[interactions["user_index"].isin(indices)].copy()
    similar_users = similar_users[similar_users["user_id"]!=str(userid)]
    # books_titles = pd.read_csv("C:/Users/mergo/Desktop/books.csv")
    # Assuming 'df' is your DataFrame
    columns_to_drop = ["Unnamed: 0","book_id"]
    books_titles1 = books_titles.drop(columns_to_drop, axis=1)
    # Assuming 'df' is your DataFrame
    books_titles1.rename(columns={'_id': 'book_id'}, inplace=True)
    book_recs = similar_users.groupby("book_id").rating.agg(['count', 'mean'])
    book_recs = book_recs.merge(books_titles1, how="inner", on="book_id")
    book_recs["adjusted_count"] = book_recs["count"] * (book_recs["count"] / book_recs["ratings"])
    book_recs["score"] = book_recs["mean"] * book_recs["adjusted_count"]
    book_recs = book_recs[book_recs["mean"] >=4]
    book_recs_list = []
    for _, row in book_recs.iterrows():
        book_rec_dict = {
            "book_id": row["book_id"],
            "title": row["title"],
            "count": row["count"],
            "mean": row["mean"],
            "adjusted_count": row["adjusted_count"],
            "score": row["score"],
            "cover_image": row["cover_image"]
        }
        book_recs_list.append(book_rec_dict)

    return jsonify(results=book_recs_list)

@app.route('/itembased/<book_title>', methods=['POST'])
def itembased(book_title):
    users_books_df = interactions.pivot_table(index='user_id', columns='title', values='rating')
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

@app.route('/year_list', methods=['GET'])
def year_list():
    # json_data = books_years_list.to_json(orient='values')
    df_list = books_years_list.values.tolist()
    updated_list = []
    for item in df_list:
        item_dict = {"year": item[0]}
        updated_list.append(item_dict)
    # JSONP_data = jsonify(df_list)
    return jsonify(results=updated_list)
@app.route('/year_books/<year>', methods=['POST'])
def year_books(year):
    year_sort = books_titles.sort_values(by='publication_year', ascending=False)
    year_sort = year_sort[year_sort['publication_year'].notna()]
    filtered_groups = year_sort[year_sort['publication_year'] == float(year)]
    book_recs_list = []
    for index, row in filtered_groups.iterrows():
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
@app.route('/popular_books', methods=['GET'])
def popular_books():
    book_recs_list = []
    for index, row in books_popular.iterrows():
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