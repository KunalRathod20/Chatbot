from flask import Flask, request, render_template
import requests
import json
from flask_restful import Api, Resource, reqparse
import pytesseract #for ocr
import cv2
from PIL import Image #image reading library
import os, werkzeug #for folders
from math import floor
import base64
import config
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
# set up API key
<<<<<<< HEAD
api_key = os.getenv("OPENAI_API_KEY")  # Store your key in an environment variable
=======



app = Flask(__name__)
api = Api(app)  #flask object
parser = reqparse.RequestParser()
parser.add_argument('file',type=werkzeug.datastructures.FileStorage, location='files')
history = ""
historyCount = 0



pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' 


REDUCTION_COEFF = 0.9
QUALITY = 85

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get", methods = ["GET"])
def generate_response_main():
    data = requests.get(f"https://example-files.online-convert.com/document/txt/example.txt")
    description = data.text
    
    user_message = request.args.get('msg')

    global history
    global historyCount
    if historyCount == 2:
        for i in range(1, len(history)):
            if history[i : i + 5] == "User:":
                history = history[i:]
                break
        historyCount -= 1

    topic = classify_botTopic(user_message)
    if topic == 'image':
        response = generate_response_botImage(user_message)
    elif topic == 'movie':
        history += "\nUser: " + user_message + "\nBrend: " 
        response = generate_response_botMovie(user_message)

        history += response
        historyCount += 1
    else:
        history += "\nUser: " + user_message + "\nBrend: " 
        prompt = description + history
        response = generate_response_botNormal(prompt)

        history += response 
        historyCount += 1
    
    return response




def generate_response(user_message, description_file=""): #text response genearation function
    if description_file == "":
        prompt = user_message
    else:   
        data = requests.get(f"https://example-files.online-convert.com/document/txt/example.txt/{description_file}")
        description = data.text
        prompt = description + user_message + "\nYou: "    

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "model": "gpt-3.5-turbo",
            "max_tokens": 350,
            "temperature": 0.4,
            "messages" : [
                {"role": "user", "content": prompt}
            ]
        },
    )

    if response.ok:
        result = response.json()["choices"][0]["message"]["content"].strip()    
        return result
    else:
        return "I'm sorry, I'm having trouble generating a response right now."




def generate_response_botImage(user_message): #to take text input from user
    result = generate_image(user_message)
    return result





def generate_response_botNormal(prompt):
    return generate_response(prompt, "")


def classify_botTopic(user_message):
    return generate_response(user_message, "botTopic.txt")


def classify_botMovieTopic(user_message):
    response = generate_response(user_message, "botMovieTopic.txt")
    return response

def generate_response_botInfo(user_message):
    response = generate_response(user_message, "botTitles.txt")
    titles = response.split('; ')

    result = ""
    if len(titles) == 0:
        return response_anyway()
    else:
        for title in titles:
            info = get_movie_info(title)
            para = generate_response_botParagraph(info)
            result += para + "\n\n"    
        return result
    

def generate_response_botSimilar(user_message):
    response = generate_response(user_message, "botTitles.txt")
    titles = response.split('; ')
    title = titles[0]

    url1 = f"https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={title}"
    response1 = requests.get(url1)
    results1 = response1.json()["results"]

    url2 = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}"
    response2 = requests.get(url2)
    results2 = response2.json()["results"]

    if len(results1) == 0 and len(results2) == 0:
        return response_anyway()
    elif len(results1) == 0:
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = []  
    elif len(results2) == 0:
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = []  
    elif float(json.dumps(results1[0]["popularity"])) >= float(json.dumps(results2[0]["popularity"])):
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = [] 
    elif float(json.dumps(results1[0]["popularity"])) < float(json.dumps(results2[0]["popularity"])):
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = [] 
    elif similarity(json.dumps(results1[0]["name"]).lower(), title.lower()) >= similarity(json.dumps(results2[0]["title"]).lower(), title.lower()):
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = [] 
    else: 
        try:
            movie_id = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}").json()["results"][0]["id"]
            movies = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={tmdb_api_key}").json()["results"]
        except:
            movies = []    

    result = ""
    if len(movies) == 0:
        return response_anyway()
    else:
        for i in range(min(3, len(movies))):
            para = generate_response_botParagraph(json.dumps(movies[i]))
            result += para + "\n\n"    
        return result

def response_anyway():
    data = requests.get(f"https://example-files.online-convert.com/document/txt/example.txt/botNormal.txt")
    description = data.text

    global history
    prompt = description + history
    return generate_response_botNormal(prompt)
    

def generate_response_botGenre(user_message):
    response = generate_response(user_message, "botGenres.txt")
    if response == 'undefined':
        return response_anyway()

    genre = response.split('; ')
    for i in range(len(genre)):
        genre[i] = genreList[genre[i]]
    
    genreTV = []
    for i in range(len(genre)):
        x = genre[i]
        if x == 28 or x == 12: x = 10759
        if x == 878 or x == 14: x = 10765
        genreTV.append(x)
    
    url1 = f"https://api.themoviedb.org/3/discover/tv?api_key={tmdb_api_key}&with_genres="
    for i in range(len(genreTV)):
        url1 += str(genreTV[i]) + ','

    url2 = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&with_genres="
    for i in range(len(genre)):
        url2 += str(genre[i]) + ','
    
    movies1 = requests.get(f"{url1}").json()["results"]
    movies2 = requests.get(f"{url2}").json()["results"]
    if len(movies1) and len(movies2) == 0:
        return response_anyway()

    result = ""
    if len(movies1) == 0:
        for i in range(min(3, len(movies2))):
            para = generate_response_botParagraph(json.dumps(movies2[i]))
            result += para + "\n\n"
    elif len(movies2) == 0:
        for i in range(min(3, len(movies1))):
            para = generate_response_botParagraph(json.dumps(movies1[i]))
            result += para + "\n\n"
    else:
        for i in range(min(2, len(movies1))):
            para = generate_response_botParagraph(json.dumps(movies1[i]))
            result += para + "\n\n"
        para = generate_response_botParagraph(json.dumps(movies2[0]))
        result += para + "\n"
    
    return result


def generate_response_botTrending(user_message):
    response = generate_response(user_message, "botGenres.txt")
    genre = response.split('; ')

    if genre[0] == "undefined":
        genre = []
    for i in range(len(genre)):
        genre[i] = genreList[genre[i]]
    
    genreTV = []
    for i in range(len(genre)):
        x = genre[i]
        if x == 28 or x == 12: x = 10759
        if x == 878 or x == 14: x = 10765
        genreTV.append(x)

    url = f"https://api.themoviedb.org/3/trending/all/week?api_key={tmdb_api_key}"
    movies = requests.get(f"{url}").json()["results"]

    result = ""
    movieCount = 0
    for i in range(len(movies)):
        if movieCount == 3: break

        cnt = 0
        for j in range(min(4, len(genreTV))):
            for k in range(len(movies[i]["genre_ids"])):
                if json.dumps(movies[i]["genre_ids"][k]) == str(genreTV[j]):
                    cnt += 1

        for j in range(min(2, len(genre))):
            for k in range(len(movies[i]["genre_ids"])):
                if json.dumps(movies[i]["genre_ids"][k]) == str(genre[j]):
                    cnt += 1

        if cnt == 0 and len(genre) != 0: continue
        para = generate_response_botParagraph(json.dumps(movies[i]))
        result += para + "\n\n"
        movieCount += 1
    
    if movieCount == 0:
        return response_anyway()

    return result
        

def generate_response_botParagraph(info):
    return generate_response(info, "botParagraph.txt")


def generate_image(user_message): #DALL E
    prompt = user_message
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "prompt": prompt,
            "n": 1,
            "size":"256x256"
        },
    )
    
    if response.ok:
        result = response.json()["data"][0]["url"].strip()  
        return result
    else:
        return "I'm sorry, I'm having trouble generating a response right now."

def similarity(s1, s2):

    # initialize a matrix with zeros
    matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
    
    # populate the matrix with edit distances
    for i in range(len(s1) + 1):
        for j in range(len(s2) + 1):
            if i == 0:
                matrix[i][j] = j
            elif j == 0:
                matrix[i][j] = i
            elif s1[i-1] == s2[j-1]:
                matrix[i][j] = matrix[i-1][j-1]
            else:
                matrix[i][j] = 1 + min(matrix[i-1][j], matrix[i][j-1], matrix[i-1][j-1])
    
    # calculate the similarity as 1 - (edit distance / max length)
    max_length = max(len(s1), len(s2))
    similarity = 1 - (matrix[len(s1)][len(s2)] / max_length)
    
    # return the similarity as a percentage
    return round(similarity * 100, 2)

@app.route('/home')
def home():
    return render_template('imageindex.html')
    



@app.route('/upload/', methods=['GET', 'POST']) #image to text
def upload():
    try:
        imagefile = request.files.get('imagefile', '')
        #create byte stream from uploaded file
        file = request.files['imagefile'].read() ## byte file
        img = Image.open(imagefile)
        img1 = img.convert('LA')
        print("Before reducing",img1.size)
        print("byte length",len(file))
        imgsize=len(file) >> 20
        print("imgsize",imgsize)
        if imgsize>2:
            x, y = img1.size
            x *= REDUCTION_COEFF
            y *= REDUCTION_COEFF
            img1 = img1.resize((floor(x),floor(y)), Image.BICUBIC)
            print("Img reduced",img1.size)
        ext = "jpeg"
        if "." in imagefile.filename:
            ext = imagefile.filename.rsplit(".", 1)[1]
        text = pytesseract.image_to_string(img1)
        #Base64 encoding the uploaded image 
        img_base64 = base64.b64encode(file)
        img_base64_str = str(img_base64)
        #final base64 encoded string
        img_base64_str = "data:image/"+ ext +";base64,"+img_base64_str.split('\'',1)[1][0:-1]
        f = open("sample.txt", "a")
        f.truncate(0)
        f.write(text)
        f.close()
        return render_template('result.html', text=text,img=img_base64_str)
    except Exception as e:
        print(e) 
        return render_template('error.html')
    
@app.route("/gettext") #get text from image
def gettext():
        with open("sample.txt") as fp:
            src = fp.read()
        return Response(
            src,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=sample.txt"})
    
# ----- API -----
class UploadAPI(Resource): #image upload API
    def get(self):
        print("check passed")
        return {"message": "API For TextExtractor"}, 200
    
    def post(self):
        data = parser.parse_args()
        if data['file'] == "":
            return {'message':'No file found'}, 400
        
        photo = data['file']
        if photo:
            photo.save(os.path.join("./static/images/",photo.filename))
            img = Image.open(photo)
            img1 = img.convert("LA")
            text = pytesseract.image_to_string(img1)
            print("check 1 passed")
            os.remove(os.path.join("./static/images/",photo.filename))
            return {"message": text}, 200
        else:
            return {'message':'Something went wrong'}, 500

api.add_resource(UploadAPI, "/api/v1/")


if __name__ == "__main__":
    app.run()