from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth 
from django.contrib.auth.decorators import login_required
import requests
from dotenv import load_dotenv
import os
load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

# Create your views here.
def api_spotify(url,params=None):

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params= params)
    return response.json()

def top_album(content):
    track_details  = []
    if 'sections' in content:
        for track in content['sections']['items'][1]['contents']['items']:
            name = track.get('name', 'Unknown')
            artist_name = track.get('artists', [{}])[0].get('name', 'Unknown')
            track_id = track.get('id', 'No ID')
            cover_url = track.get('cover', [{}])[0].get('url', 'No Url')
            track_details.append({
                'id': track_id,
                'name': name,
                'artist': artist_name,
                'cover_url': cover_url
            })
    return track_details 

def top_artists(content):
    artists_info = []
    if 'sections' in content:
        for artist in content['sections']['items'][0]['contents']['items'][:8]:
            name = artist.get('name', 'Unknown')
            avatar_url = artist.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No URL')
            artist_id = artist.get('id', 'No ID')
            artists_info.append((name, avatar_url, artist_id))

    return artists_info

def music(request,pk):
    content = api_spotify(url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata", params = {"trackId":pk})
    print(content)
    track_name = content['name']
    artist_name = content['artists'][0]['name']
    image_url = content['album']['cover'][1]['url']
    duration = content.get('durationText')
    audio = api_spotify(url = 'https://spotify-scraper.p.rapidapi.com/v1/track/download', params = {'track': track_name + artist_name})
    audio_url = audio['youtubeVideo']['audio'][0]['url']
    context = {
        'track_name': track_name,
        'artist_name': artist_name,
        'track_image':image_url,
        'audio_url' : audio_url,
        'duration_text': duration,
    }
    return render(request, 'music.html',context)

def profile(request,pk):

    data = api_spotify(url = 'https://spotify-scraper.p.rapidapi.com/v1/artist/overview', params = {"artistId":pk})
    name = data['name']
    month_view = data['stats']['monthlyListeners']
    header_url = data['visuals']['header'][0]['url']
    top_tracks = []
    for track in data['discography']['topTracks']:
        trackid = track['id']
        trackname = track['name']
        img = track['album']['cover'][0]['url']
        
        track_info ={
            'id': trackid,
            'name': trackname,
            'durationText': track['durationText'],
            'playCount': track['playCount'],
            'track_image':img,
        }
        top_tracks.append(track_info)

    context = {
        'name':name,
        "monthlyListeners": month_view,
        'headerUrl':header_url,
        'topTracks': top_tracks,
    }
    return render(request, 'profile.html',context)
def search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        data = api_spotify(url = 'https://spotify-scraper.p.rapidapi.com/v1/search', params = {"term":search_query, 'type':'track'})
        result_count = data['tracks']['totalCount']
        track_list =[]
        for track in data['tracks']['items']:
            trackname = track['name']
            artistname = track['artists'][0]['name']
            durationText = track['durationText']
            trackid = track['id']
            img = track['album']['cover'][0]['url']
            track_list.append({
                'track_name': trackname,
                'artist_name': artistname,
                'duration': durationText,
                'trackid': trackid,
                'track_image': img,
            })
        context = {
            'search_results_count': result_count,
            'track_list': track_list,
        }
        return render(request,'search.html',context)
    else:
        return render(request, 'search.html')

@login_required(login_url= 'login')
def index(request):
    content = api_spotify(url = "https://spotify-scraper.p.rapidapi.com/v1/home")
    artis_info = top_artists(content = content)
    top_album_list = top_album(content = content)
    one_third_track_list = int(len(top_album_list)/3)
    # divide the list into three parts
    first_six_tracks = top_album_list[:one_third_track_list]
    second_six_tracks = top_album_list[one_third_track_list:len(top_album_list) - one_third_track_list]
    third_six_tracks = top_album_list[len(top_album_list) - one_third_track_list:]

    context = {
        "artists_info": artis_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }
    return render(request, 'index.html',context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_login = auth.authenticate(username = username, password = password)
        if user_login is not None:
            auth.login(request,user_login)
            return redirect('/')
        else:
            messages.info(request,'Invalid username or password!')
            return redirect('login')
    else:
        return render(request, 'login.html')

@login_required(login_url= 'login')
def logout(request):
    auth.logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists!')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists!')
                return redirect('signup')
            else:
                user = User.objects.create_user(username = username, email = email, password = password)
                user.save()
                user_login = auth.authenticate(username = username, password = password)
                auth.login(request,user_login)
                return redirect('/')
        else:
            messages.info(request,'Password not match!')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

