import pymongo
import nltk
import pandas as pd
from bson.objectid import ObjectId
nltk.download("stopwords")
from flask import Flask, request, jsonify

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
client_books = pymongo.MongoClient(url)
db_books = client_books['book']
collection_book = db_books['books']
mongo_book_title = []
for data in mongo_book_id:
    books = collection_book.find_one({'_id': ObjectId(data)})
    mongo_book_title.append(books['title'])
new_user = pd.DataFrame({'user_id':userid,'book_id': book_ids, 'rating': ratings,'title':mongo_book_title})
client.close()


print(new_user)
@app.route('/')
def home():
    return 'Server works'

@app.route('/recommendations', methods=['GET'])
def recommendations():
    books_df = pd.read_csv(r'C:\Users\mergo\Desktop\data\\books.csv')
    ratings_df = pd.read_csv(r'C:\Users\mergo\Desktop\data\\ratings.csv')
    other_users = ratings_df[ratings_df['book_id'].isin(new_user['book_id'].values)]
    # Sort users by count of most mutual books with me
    users_mutual_books = other_users.groupby(['user_id'])
    users_mutual_books = sorted(users_mutual_books, key=lambda x: len(x[1]), reverse=True)
    # Pearson correlation
    from scipy.stats import pearsonr

    pearson_corr = {}

    for user_id, books in ratings_df:
        # Books should be sorted
        books = books.sort_values(by='book_id')
        book_list = books['book_id'].values

        new_user_ratings = new_user[new_user['book_id'].isin(book_list)]['rating'].values
        user_ratings = books[books['book_id'].isin(book_list)]['rating'].values

        corr = pearsonr(new_user_ratings, user_ratings)
        pearson_corr[user_id] = corr[0]
    # Get top50 users with the highest similarity indices
    pearson_df = pd.DataFrame(columns=['user_id', 'similarity_index'], data=pearson_corr.items())
    pearson_df = pearson_df.sort_values(by='similarity_index', ascending=False)[:50]
    # Get all books for these users and add weighted book's ratings
    users_rating = pearson_df.merge(ratings_df, on='user_id', how='inner')
    users_rating['weighted_rating'] = users_rating['rating'] * users_rating['similarity_index']
    # Calculate sum of similarity index and weighted rating for each book
    grouped_ratings = users_rating.groupby('book_id').sum()[['similarity_index', 'weighted_rating']]
    recommend_books = pd.DataFrame()

    # Add average recommendation score
    recommend_books['avg_reccomend_score'] = grouped_ratings['weighted_rating'] / grouped_ratings['similarity_index']
    recommend_books['book_id'] = grouped_ratings.index
    recommend_books = recommend_books.reset_index(drop=True)

    # Left books with the highest score
    recommend_books = recommend_books[(recommend_books['avg_reccomend_score'] == 5)]
    # Let's see our recomendations
    recommendation = books_df[books_df['book_id'].isin(recommend_books['book_id'])][
        ['authors', 'title', 'book_id']].sample(10)
    return recommend_books.to_html()
if __name__ == "__main__":
    app.run()
