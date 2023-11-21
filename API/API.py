from flask import Flask, jsonify, request
import pandas as pd
import sys 

sys.path.append('API/RawData') 

app = Flask(__name__)

# Function to read data files
def read_data_files():
    u_data = pd.read_csv('u.data', sep='\t', names=['userId', 'movieId', 'rating', 'timestamp'])
    u_item = pd.read_csv('u.item', sep='|', encoding='latin-1', header=None, names=['movieId', 'title', 'release_date', 'video_release_date', 'IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
    u_user = pd.read_csv('u.user', sep='|', names=['userId', 'age', 'gender', 'occupation', 'zipcode'])
    return u_data, u_item, u_user

# Function to extract genres for each movie
def extract_genres(row):
    genres = ['unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    movie_genres = [genre for genre, val in zip(genres, row[5:]) if val == 1]
    return movie_genres

# Function to create JSON entry
def create_json_entry(row):
    return {
        "userId": str(row['userId']),
        "movie": {
            "movieId": str(row['movieId']),
            "title": row['title'],
            "genres": row['genres']
        },
        "rating": str(row['rating']),
        "timestamp": str(row['timestamp'])
    }


@app.route('/movie_data', methods=['GET'])
def get_movie_data():
    u_data, u_item, u_user = read_data_files()

    # Apply genre extraction function to each row in u_item
    u_item['genres'] = u_item.apply(extract_genres, axis=1)

    # Merge relevant data
    merged_data = pd.merge(u_data, u_item[['movieId', 'title', 'genres']], on='movieId')
    merged_data = pd.merge(merged_data, u_user[['userId', 'age', 'gender', 'occupation']], on='userId')

    # Convert to JSON format
    json_data = merged_data.apply(create_json_entry, axis=1).tolist()

    yield jsonify(json_data)

if __name__ == '__main__':
    app.run(debug=True)