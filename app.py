from flask import Flask, request, jsonify
import requests
import joblib

from flask import Flask, request
import joblib


app = Flask(__name__)
# model = joblib.load('Collaborative_Filtering.py')

# Replace with your ML model code to generate recommendations
def get_recommendations(userid):
    # Code to generate recommendations for the given userid
    model = joblib.load('Collaborative_Filtering.py')
    Collaborative_Filtering.make_clickable()
    return ["rec1", "rec2", "rec3"]

@app.route('/recommendations')
def get_recommendations_route():
    # Get the userid parameter from the request
    userid = request.args.get('userid')

if __name__ == '__main__':
    app.run()