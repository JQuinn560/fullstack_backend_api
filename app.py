from flask import Flask, make_response, jsonify, request
import uuid, random
import jwt
import datetime
from functools import wraps


def jwt_required(func):
    @wraps(func)
    def jwt_requried_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify( { 'message' : ' Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify( { 'message' : ' Token is invalid'}), 401
        return func(*args, **kwargs)
    return jwt_requried_wrapper

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'

@app.route("/", methods = ["GET"])
def index():
    return make_response("<h1>Hello</h1>", 200)

movies = {}

def generate_dummy_data():
    genres =['comedy', 'action', 'scifi', 'romance']

    movie_dict = {}

    for i in range(100):
        id = str(uuid.uuid1())
        name = 'Lol ' + str(i)
        genre = genres[random.randint(0, len(genres)-1)]
        rating = random.randint(1,10)
        movie_dict[id] = {
            "name" : name,
            "genre" : genre,
            "rating" : rating,
            "reviews" : []
        }
    return movie_dict


#show all movies
@app.route("/api/v1.0/movies", methods = ["GET"])
def show_all_movies():
    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get('pn'))
    if request.args.get("ps"):
        page_num = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))
    movies_list = [{k:v}for k, v in movies.items()]
    data_to_return  = movies_list[page_start:page_start+page_size]
    return make_response( jsonify( data_to_return ) )

#show one movie by id
@app.route("/api/v1.0/movies/<string:id>", methods = ["GET"])
@jwt_required
def show_one_movie(id):
    if id in movies:
        return make_response( jsonify( movies[id]), 200)
    else: 
        return make_response( jsonify ( { "error" : "invalid Movie Id"} ), 404 )

#add a new movie
@app.route("/api/v1.0/movies", methods = ["POST"])
def add_new_movie():
    if "name" in request.form and "genre" in request.form and "rating" in request.form:
        next_id = str(uuid.uuid1())
        new_movie = {
            "name": request.form["name"],
            "genre": request.form["genre"],
            "rating": request.form["rating"],
            "reviews": {}
    }
        movies[next_id]= new_movie
        return make_response( jsonify( { next_id : new_movie } ), 201)
    else: 
        return make_response( jsonify ( { "error" : "Missing form data"} ), 404 )

#edit movie details
@app.route("/api/v1.0/movies/<string:id>", methods = ["PUT"])
def edit_movie(id):
    if id not in movies:
        return make_response( jsonify ( { "error" : "invalid Movie Id"} ), 404 )
    else:
        if "name" in request.form and "genre" in request.form and "rating" in request.form:
            movies[id]["name"] = request.form["name"]
            movies[id]["genre"] = request.form["genre"]       
            movies[id]["rating"] = request.form["rating"]
            return make_response( jsonify( { id : movies[id] } ), 200 )
        else:
             return make_response( jsonify ( { "error" : "Missing form data"} ), 404 )


#delete movie
@app.route("/api/v1.0/movies/<string:id>", methods = ["DELETE"])
def delete_movie(id):
    if id in movies:
        del movies[id]
        return make_response( jsonify( {} ), 204 )
    else:
        return make_response( jsonify ( { "error" : "invalid Movie Id"} ), 404 )


#get all reviews of a movie
@app.route("/api/v1.0/movies/<string:id>/reviews", methods = ["GET"])
def fetch_all_reviews(id):
  return make_response( jsonify ( movies[id]["reviews"] ), 200)

#add a review on a movie
@app.route("/api/v1.0/movies/<string:id>/reviews", methods = ["POST"])
def add_new_review(id):
    new_review_id = str( uuid.uuid1())
    new_review = {
        "username" : request.form["username"],
        "comment" : request.form["comment"],
        "rating" : request.form["rating"]
    }
    movies[id]["reviews"][new_review_id] = new_review
    return make_response( jsonify ( {new_review_id : new_review } ), 201)


#get one review of a movie
@app.route("/api/v1.0/movies/<string:id>/reviews/<string:reviewID>", methods = ["GET"])
def fetch_one_review(id, reviewID):

    return make_response( jsonify ( movies[id]["reviews"][reviewID] ), 200)


#edit a review on a movie
@app.route("/api/v1.0/movies/<string:id>/reviews/<string:reviewID>", methods = ["PUT"])
def edit_review(id, reviewID):
    movies[id]["review"][reviewID]["username"] = request.form["username"]
    movies[id]["review"][reviewID]["comment"] =  request.form["comment"]
    movies[id]["review"][reviewID]["rating"] = request.form["rating"]
    return make_response( jsonify ({ reviewID: movies[id]["review"][reviewID]}), 200)


#delete a review of a movie
@app.route("/api/v1.0/movies/<string:id>/reviews/<string:reviewID>", methods = ["DELETE"])
def delete_review(id, reviewID):
    del movies[id]["reviews"][reviewID]
    return make_response( jsonify ( {} ), 204)



#json web token
@app.route("/api/v1.0/login", methods = ["GET"])
def login():
    auth = request.authorization
    if auth and auth.password == 'password':
        token = jwt.encode( {
            'user' : auth.username,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        return jsonify( { 'token' : token }) 
    return make_response('could not verify', 401, {
        'WWW-Authenticate' : 'Basic realm = "Login required"'
    })



if __name__ == "__main__":
    movies = generate_dummy_data()
    app.run(debug= True)