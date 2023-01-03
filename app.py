from flask import Flask, render_template, request
import pickle
import numpy as np

popularity_df = pickle.load(open('model/popularity_df.pkl', 'rb'))
pivoted_df = pickle.load(open('model/pivoted_df.pkl', 'rb'))
books = pickle.load(open('model/books.pkl', 'rb'))
similarity_score = pickle.load(open('model/similarity_score.pkl', 'rb'))

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',
                           book_name=popularity_df['Book-Title'],
                           author_name=popularity_df['Book-Author'],
                           book_cover_url=popularity_df['Image-URL-M'],
                           average_ratings=popularity_df['Avg_ratings'].round(decimals=2))

@app.route('/recommend', methods=['GET', 'POST'])
def recommend_ui():
    return render_template('recommend.html',
                           books=list(books['Book-Title']))
@app.route('/recommend_books', methods=['POST'])
def recommend():
    response = {}
    data = []
    item = []
    user_input = request.form.get('Book_Name')

    # fetch index
    index = np.where(pivoted_df.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:9]

    # Fetch book title, author and image URL for the selected book
    temp_df = books[books['Book-Title'] == user_input]
    item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
    item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
    item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
    data.append(item)
    response['Selected-Book'] = data

    # Fetch recommendations
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pivoted_df.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)
    response['Recommended-Books'] = data

    return render_template('recommend.html',
                           data=response)

if __name__ == '__main__':
    app.run(debug=True)