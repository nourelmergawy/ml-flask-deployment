import numpy as np
from flask import Flask, request
import onnxruntime as rt
import pandas as pd
import pymongo

app = Flask(__name__)

# Load the ONNX model
sess = rt.InferenceSession("resnet18.onnx")

# Define the input and output names for the model
input_name = sess.get_inputs()[0].userid
output_name = sess.get_outputs()[0].name


def test_model(user_id):
    # get user id
     user_id =4

@app.route('/')
def home():
    return 'Server works'


@app.route('/recommendations', methods=['POST'])
def recommendations():
    user_id = request.args['user_id']
    test_model(user_id)

def connectmongo():
    import pandas as pd
    import pymongo

    # Specify the database URL and credentials
    url = "mongodb+srv://maryam:recobooks@cluster0.fhsy9vt.mongodb.net/?retryWrites=true&w=majority"

    # Create a client object
    client = pymongo.MongoClient(url)

    # Access the database
    db = client.dbname
    # Access the collection
    collection = db.collection_name

    # Retrieve the data
    data = collection.find()
    for document in data:
        # Do something with the document
        print(document)

    # Convert the data into a Pandas DataFrame
    my_books = pd.DataFrame(list(data))
    document(2)
    # Close the connection
    client.close()

if __name__ == '_main_':
    app.run(debug=True)