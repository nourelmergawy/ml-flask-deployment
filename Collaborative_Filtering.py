#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
my_books = pd.read_csv("liked_books.csv", index_col =0)

my_books["book_id"] = my_books["book_id"].astype(str)

# In[5]:

csv_book_mapping = {}
with open("book_id_map.csv","r") as f:
    while True:
        line = f.readline()
        if not line:
            break
        csv_id , book_id = line.strip().split(",")
        csv_book_mapping[csv_id] = book_id


# In[6]:


book_set = set(my_books["book_id"])

# In[8]:


overlap_users = {}

with open("goodreads_interactions.csv", 'r') as f:
    while True:
        line = f.readline()
        if not line:
            break
        user_id, csv_id, _, rating, _ = line.split(",")
        
        book_id = csv_book_mapping.get(csv_id)
        
        if book_id in book_set:
            if user_id not in overlap_users:
                overlap_users[user_id] = 1
            else:
                overlap_users[user_id] += 1


# In[9]:


len(overlap_users)


# In[10]:


filtered_overlap_users = set([k for k in overlap_users if overlap_users[k] > my_books.shape[0]/5])


# In[11]:


len(filtered_overlap_users)


# In[12]:


interactions_list = []

with open("goodreads_interactions.csv", 'r') as f:
    while True:
        line = f.readline()
        if not line:
            break
        user_id, csv_id, _, rating, _ = line.split(",")
        
        if user_id in filtered_overlap_users:
            book_id = csv_book_mapping[csv_id]
            interactions_list.append([user_id, book_id, rating])


# In[13]:


len(interactions_list)


# In[14]:


interactions_list[0]


# In[15]:


interactions = pd.DataFrame(interactions_list, columns=["user_id", "book_id", "rating"])


# In[16]:


interactions = pd.concat([my_books[["user_id", "book_id", "rating"]], interactions])


# In[17]:


interactions


# In[18]:


interactions["book_id"] = interactions["book_id"].astype(str)
interactions["user_id"] = interactions["user_id"].astype(str)
interactions["rating"] = pd.to_numeric(interactions["rating"])


# In[19]:


interactions["user_id"].unique()


# In[20]:


interactions["user_index"] = interactions["user_id"].astype("category").cat.codes


# In[21]:


interactions["book_index"] = interactions["book_id"].astype("category").cat.codes


# In[22]:


from scipy.sparse import coo_matrix

ratings_mat_coo = coo_matrix((interactions["rating"], (interactions["user_index"], interactions["book_index"])))


# In[23]:


ratings_mat_coo.shape


# In[24]:


ratings_mat = ratings_mat_coo.tocsr()


# In[25]:


interactions[interactions["user_id"] == "-1"]


# In[26]:


my_index = 0


# In[27]:


from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(ratings_mat[my_index,:], ratings_mat).flatten()


# In[28]:


similarity[0]


# In[29]:


import numpy as np

indices = np.argpartition(similarity, -15)[-15:]


# In[30]:


indices


# In[31]:


similar_users = interactions[interactions["user_index"].isin(indices)].copy()


# In[32]:


similar_users = similar_users[similar_users["user_id"]!="-1"]


# In[33]:


similar_users


# In[34]:


book_recs = similar_users.groupby("book_id").rating.agg(['count', 'mean'])


# In[35]:


book_recs


# In[36]:


books_titles = pd.read_json("book_titles.json")
books_titles["book_id"] = books_titles["book_id"].astype(str)


# In[37]:


book_recs = book_recs.merge(books_titles, how="inner", on="book_id")


# In[38]:


book_recs


# In[39]:


book_recs["adjusted_count"] = book_recs["count"] * (book_recs["count"] / book_recs["ratings"])


# In[40]:


book_recs["score"] = book_recs["mean"] * book_recs["adjusted_count"]


# In[41]:


book_recs = book_recs[~book_recs["book_id"].isin(my_books["book_id"])]


# In[42]:


my_books["mod_title"] = my_books["title"].str.replace("[^a-zA-Z0-9 ]", "", regex=True).str.lower()


# In[43]:


my_books["mod_title"] = my_books["mod_title"].str.replace("\s+", " ", regex=True)


# In[44]:


book_recs = book_recs[~book_recs["mod_title"].isin(my_books["mod_title"])]


# In[45]:


book_recs = book_recs[book_recs["mean"] >=4]


# In[46]:


book_recs = book_recs[book_recs["count"]>2]


# In[47]:


top_recs = book_recs.sort_values("mean", ascending=False)


# In[48]:


def make_clickable(val):
    return '<a target="_blank" href="{}">Goodreads</a>'.format(val, val)

def show_image(val):
    return '<a href="{}"><img src="{}" width=50></img></a>'.format(val, val)

top_recs.style.format({'url': make_clickable, 'cover_image': show_image})


# In[3]:
