from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth 
from django.contrib.auth.decorators import login_required
import requests
# Create your views here.
def api_spotify():
    url = "https://spotify-scraper.p.rapidapi.com/v1/home"

    headers = {
        "x-rapidapi-key": "8081fc2457msh951f68a0584220dp1815fdjsn6b10b117d431",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def top_tracks(content):
    track_details  = []
    if 'sections' in content:
        for track in content['sections']['items'][1]['contents']['items']:
            name = track.get('name', 'No Name')
            artist_name = track.get('artists', [{}])[0].get('name', 'No Name')
            track_id = track.get('id', 'No ID')
            cover_url = track.get('cover', [{}])[0].get('url', 'No Url')
            track_details.append({
                'id': track_id,
                'name': name,
                'artist': artist_name,
                'cover_url': cover_url
            })

    print(track_details)
    return track_details 

def top_artists(content):
    artists_info = []
    if 'sections' in content:
        for artist in content['sections']['items'][0]['contents']['items'][:8]:
            name = artist.get('name', 'No Name')
            avatar_url = artist.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No URL')
            artist_id = artist.get('id', 'No ID')
            artists_info.append((name, avatar_url, artist_id))

    return artists_info

def music(request,pk):
    return render(request, 'music.html')

@login_required(login_url= 'login')
def index(request):
    content = api_spotify()
    artis_info = top_artists(content = content)
    top_track_list = top_tracks(content = content)
    one_third_track_list = int(len(top_track_list)/3)
    # divide the list into three parts
    first_six_tracks = top_track_list[:one_third_track_list]
    second_six_tracks = top_track_list[one_third_track_list:len(top_track_list) - one_third_track_list]
    third_six_tracks = top_track_list[len(top_track_list) - one_third_track_list:]

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

