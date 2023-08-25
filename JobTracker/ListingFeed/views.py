import time
import asyncio
from asgiref.sync import sync_to_async
import threading
import ast
import json
import requests
import feedparser
from pathlib import Path
from . import models
from django.apps import apps
from .forms import DistanceValueForm, PhraseListForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt

BASE_DIR = Path(__file__).resolve().parent.parent

config = json.load(open(f"{BASE_DIR}/config.json"))
API_KEY = config['GOOGLE_API_KEY']


# Create your views here.


def get_city_state_from_coordinates(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        results = data['results']
        if results:
            address_components = results[0]['address_components']
            city = next((comp['long_name'] for comp in address_components if 'locality' in comp['types']), None)
            state = next((comp['short_name'] for comp in address_components if 'administrative_area_level_1' in comp['types']), None)
            return city, state
    
    return None, None


def create_indeed_url(request):
    url_prefix = f"http://rss.indeed.com/rss?q="

    profile = apps.get_model('User', 'profile')
    user_location = profile.objects.get(id=request.user.id).location
    user_location = profile.objects.get(id=request.user.id).location.strip("()").split(',')
    user_location = tuple(map(float, user_location))
    city, state = get_city_state_from_coordinates(user_location[1], user_location[0])
    city  = city.replace(" ", "+")
    user_distance = profile.objects.get(id=request.user.id).distance

    url_suffix = f"&l={city}%2C+{state}&radius={user_distance}"

    raw_phrases = models.PhraseList.objects.filter(user_id = request.user.id)
    phrase_list = []
    url_list = []
    for a in raw_phrases:
         phrase_list.append(ast.literal_eval(a.phrases))

    for query in phrase_list:
        for job_title  in query:
            job_title = job_title.replace(" ", "+")
            url = url_prefix + job_title + url_suffix
            url_list.append(url)
            print(url)

    for url in url_list:
        readable_name = url.replace("+", " ")

        db_url_entry = models.Urls(category_name=readable_name, keywords=readable_name, url=url, user_id=request.user)
        db_url_entry.save()



    



def extract_coordinates(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        coordinates = get_coordinates_from_address(address)
        return JsonResponse({'coordinates': coordinates})

    #return render(request, 'address_form.html')

def get_coordinates_from_address(address):
    base_url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'format': 'json',
        'q': address
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return {'latitude': lat, 'longitude': lon}
    return None

def update_range_value(request):
    if request.method ==  'POST':
        distance_value = request.POST.get('distanceValue')
        return int(distance_value)

def readURLList():
    file = open("./urls.txt", "r")
    urls = file.readlines()
    return urls

def parser(request):
    #urls = readURLList()
    print("Parser running")
    urls = []
    raw_url_queryset = models.Urls.objects.filter(user_id = request.user.id).values()
    for url in raw_url_queryset:
        urls.append(url.get('url'))



    responses = []

    profile = apps.get_model('User', 'profile')
    for url in urls:
        #a = client.get(url)
        b = feedparser.parse(url)
        user_location = profile.objects.get(id=request.user.id).location.strip("()").split(',')
        user_location = tuple(map(float, user_location))
        #user_location[0] = "{:.2f}".format(user_location[0])  
        #user_location[1] = "{:.2f}".format(user_location[1])  
    
        for i in b.entries:
            if len(models.Indeedlistings.objects.filter(pk=i.id)) == 0: # Check if entry exists

                #responses.append(i)
                print("recording entry...")

                inverted_gps = (i.where.coordinates[1], i.where.coordinates[0])
                d = distance(user_location, inverted_gps)

                entry = models.Indeedlistings(
                    listing_id = i.id,
                    title = i.title,
                    category_id = "",#TODO
                    location = f"POINT{i.where.coordinates}",
                    distance = d[0],
                    eta = d[1],
                    summary = i.summary,
                    link = i.links[0].href,
                    flag = False,
                    remove = False,
                    finish = False,
                    in_progress = False,
                    user_id = request.user.id
                )
                print(i.id, "\n", i.title, "\n" , i.links[0].href, "\n", i.published, "\n", i.summary, "\n",i.where.type, " - ", i.where.coordinates  ,"RECORDED IN RESPONSES LIST\n\n")

                entry.save()

        b = None
        time.sleep(15)
    print("processing complete!")
    #return render(request, "ListingFeed/feed.html")
    return HttpResponse(status=200)

def distance(fr: tuple, to: tuple):
    start = f"{fr[1]},{fr[0]}"
    end= f"{to[0]},{to[1]}"
    GOOGLE_API_ENDPOINT = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={API_KEY}"
    response = requests.get(GOOGLE_API_ENDPOINT)
    data = response.json()
    #print(data)
    print(len(data['routes']))
    if data['routes'][0]['legs'][0]['duration']['text']:
        travel_time = int(data['routes'][0]['legs'][0]['duration']['text'].replace(" mins", ""))
        distance = float(data['routes'][0]['legs'][0]['distance']['text'].replace(" mi", ""))
        #print(f"The estimated travel time by car is: {travel_time}")
        #print(f"The estimated distance by car is: {distance}")
        d = (distance, travel_time)

        return d
    else :
        return (None, None)

def feed(request):

    ## Sorting Options
    sort_param = request.GET.get('sort', 'listing_id')
    reverse_flag = request.GET.get('reverse', False)
    if sort_param == 'title' or sort_param == 'distance' or sort_param == 'eta':
        if reverse_flag == 'True':
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, finish=0, remove=0).order_by(order_by)
        else:
            order_by = f"{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, finish=0, remove=0).order_by(order_by)
    elif sort_param == 'flag':
        if reverse_flag == 'True':
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, flag=1, remove=0, finish= 0).order_by(order_by)
        else:
            order_by = f"-{sort_param}"

            entries = models.Indeedlistings.objects.filter(user_id=request.user, finish=0, remove=0).order_by(order_by)

    elif sort_param == 'remove':
        if reverse_flag == 'True':
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, remove=1).order_by(order_by)
        else:
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, remove=0, finish=0).order_by(order_by)

    elif sort_param == 'finish':
        if reverse_flag == 'True':
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user,  finish=1).order_by(order_by)
        else:
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, remove=0, finish=0).order_by(order_by)

    elif sort_param == 'in_progress':
        if reverse_flag == 'True':
            order_by = f"-{sort_param}"
            entries = models.Indeedlistings.objects.filter(user_id=request.user, in_progress=1).order_by(order_by)
        else:
            order_by = f"-{sort_param}"

            entries = models.Indeedlistings.objects.filter(user_id=request.user, in_progress=0).order_by(order_by)


    else:
        order_by = 'listing_id'
        entries = models.Indeedlistings.objects.filter(user_id=request.user, remove=0, finish=0).order_by(order_by)





    ## Datum Manipulation Buttons
    if 'search' in request.POST:
        entries = models.Indeedlistings.objects.filter(user_id=request.user, title__icontains=request.POST['search'])

    if 'flag' in request.POST:
        entry = models.Indeedlistings.objects.get(listing_id=request.POST['flag'], user_id=request.user)
        entry.flag = 0 if entry.flag == 1 else 1
        entry.save()
        print(request.POST)
    elif 'remove' in request.POST:
        entry = models.Indeedlistings.objects.get(listing_id=request.POST['remove'], user_id=request.user)

        entry.remove = 0 if entry.remove == 1 else 1
        entry.save()

        entries = models.Indeedlistings.objects.exclude(remove=1, user_id=request.user).values()
        context = {"entries": entries,}
        print(request.session)
    elif 'done' in request.POST:
        entry = models.Indeedlistings.objects.get(listing_id=request.POST['done'], user_id=request.user)
        entry.finish = 0 if entry.finish== 1 else 1
        entry.save()
        entries = models.Indeedlistings.objects.exclude(finish=1, user_id=request.user).values()
        context = {"entries": entries,}
        print(request.POST)
    elif 'inprogress' in request.POST:
        entry = models.Indeedlistings.objects.get(listing_id=request.POST['inprogress'], user_id=request.user)
        entry.in_progress = 0 if entry.in_progress == 1 else 1
        entry.save()
        print(request.POST)

    context = {"entries": entries, 'reverse_flag':reverse_flag}
    
    return render(request, "ListingFeed/feed.html", context)


def fetch(request):
    parser(request)
    context = {}
    return render(request, "ListingFeed/fetch.html", context)


def manage(request):
    profile = apps.get_model('User', 'profile')
    distForm = DistanceValueForm()
    plistForm = PhraseListForm()
    
    if 'distanceForm' in request.POST:
        distForm = DistanceValueForm(request.POST)
        distance_value = request.POST.get('distanceValue')
        userdistance = profile.objects.get(id = request.user.id)
        userdistance.distance = distance_value
        userdistance.save()
        if distForm.is_valid():
            print(distance_value)

        else: 
            distForm = DistanceValueForm()


    if 'getGPS' in request.POST:
        address = request.POST.get('address')
        coordinates = get_coordinates_from_address(address)
        print(coordinates['longitude'], coordinates['latitude'])
        location = (coordinates['longitude'], coordinates['latitude'])
        userprofile = profile.objects.get(id = request.user.id)
        userprofile.location = location
        userprofile.save()


    if 'getURLS' in request.POST:
        create_indeed_url(request)

    if 'queryKeywords' in request.POST:
        plistForm = PhraseListForm(request.POST)
        if plistForm.is_valid():

            plist = plistForm.save(commit=False)
            plist.user_id = request.user
            plist.save()


        else: 
            plistForm = PhraseListForm()


    raw_phrases = models.PhraseList.objects.filter(user_id = request.user.id)
    phrase_list = []
    for a in raw_phrases:
         phrase_list.append(ast.literal_eval(a.phrases))

    context = {
            "rangeForm":distForm,
            "PhraseListForm": plistForm,
            "PhraseList": phrase_list,
            "url_list": models.Urls.objects.filter(user_id = request.user).values()
    }

    if 'procList' in request.POST:
        return redirect("loading")

    if 'startParsingButton' in request.POST:
    #if request.method == "POST":
        print("start thread")
        parser_thread = threading.Thread(target=parser, args=(request,))
        parser_thread.start()
        parser_thread.join()
        print("start_parsing success")
        return redirect("feed")
        

    return render(request, "ListingFeed/manage.html", context)


def loading(request):
    return render(request, "global/loading.html")

def start_parsing(request):

    if 'startParsingButton' in request.POST:
    #if request.method == "POST":
        print("start thread")
        parser_thread = threading.Thread(target=parser, args=(request,))
        parser_thread.start()
        parser_thread.join()
        print("start_parsing success")
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "success"})

