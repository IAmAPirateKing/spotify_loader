from flask import Flask, request, render_template
import requests, json, tokens, ffmpeg, os
from pytube import YouTube

"""
    all the other junk
"""
#a place to come back to
DEFAULT_DIRECTORY = os.getcwd()
#       -   -   -   -   -   - SPOTIFY - -   -   -   -   -   -   -   
def get_playlist(token, pid):
    request_link = "https://api.spotify.com/v1/playlists/"+pid+"?fields=tracks.items(track(name, artists(name)))"#track(name),
    headers = {"Authorization":("Bearer "+token)}
    #spotify web api response
    response = requests.get(request_link, headers = headers)
    #turns response into object
    res = json.loads(response.text)["tracks"]["items"]
    return res
#   -   -   -   -   -   -   -  YOUTUBE -   -   -   -   -   -
def get_links(lst):
    res = []
    response = None
    for i in lst:
        q = (i["track"]["name"] +" - "+ i["track"]["artists"][0]["name"])
        try:
            response = requests.get("https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q="+q+"&key="+tokens.YOUTUBE_API_TOKEN)
            res.append("https://www.youtube.com/watch/?v="+json.loads(response.text)["items"][0]["id"]["videoId"])
        except:
            print("Youtube api error!")
    return res
#   -   -   -   -   -   -   -   -    PYTUBE   -   -   -   -   -   -   -   -   -
def load_tracks(lst):
    res = []
    #change working dir for download
    os.chdir("download")
    for i in lst:
        try:
            filename = YouTube(i).streams.last().download()
            res.append(filename)
        except:
            print("Pytube download Error")
    #global DEFAULT_DIRECTORY
    #os.chdir(DEFAULT_DIRECTORY)
    return res

#   -  -   -   -   -   -   -   -       FFMPEG  -   -   -   -   -       -   -   -   -
def convert_all(lst):
    for i in lst:
        (ffmpeg.input(i).output(i+".mp3").run())
        os.remove(i)
    global DEFAULT_DIRECTORY
    os.chdir(DEFAULT_DIRECTORY)
#   -   -       -   -   -   -   -   -  FLASK -   -   --  -   -   -   -   -   -   -
app = Flask(__name__)

#-  -   -   -   -   -   -   -   -   -   -   
@app.after_request
def whatever(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
# -   -   -   -   -   HOMEPAGE  -   -   -   -   -   -
@app.route("/")
def entry_point():
       return render_template("def.html") #page sends auth request to spotify and returns token as parameter to callback page
#obtains token and playlist id
@app.route("/callback")
def main():
    return render_template("index.html")

#inits download process
@app.route("/init", methods = ["POST"])
def init():
    data = (str(request.data)[2:-1].split("&"))
    #-  -   -   -       -  youtube links obtained from spotify playlist through API`s -   -  -   -   -   -   
    links = get_links(get_playlist(data[0], data[2]))
    files = load_tracks(links)
    convert_all(files)
    return "Done!"


if __name__ == "__main__":
    app.run(debug=True)
