from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
import requests
from . import forms
from . import models

# Create your views here.

def home(request):
    return render(request, 'User/home.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            retVals = {
                'username': username,
                'password': password,
                'error': True,
                'modalTitle': 'Invalid Login',
                'modalText': 'The username and password combination that you entered was invalid. Please try again. If this continues, please contact support by clicking the "Contact Us" link at the bottom of the page.',
                'modalBtnText': "Close",
                'modalImmediate': True
            }
            return render(request, 'User/login.html', retVals)

    context = {}
    return render(request, 'User/login.html')




def logoutPage(request):
    # The following also clears session data
    logout(request)
    return redirect('home')


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

def registrationPage(request):
    # print(request.session.session_key)
    # print(request.session['visitorIP'])
    user_form = forms.userRegistrationForm()
    address_form = forms.AddressForm()
    if request.method == 'POST':
        # Prepare the session and the forms.
        user_form = forms.userRegistrationForm(request.POST)
        address_form = forms.AddressForm(request.POST)
        # Check for Validation errors and send them back to the page
        if not user_form.is_valid() and not address_form.is_valid():
            print(user_form.errors)
            return render(request, 'User/register.html', {'user_form': user_form, 'address_form': address_form, 'feedback': "Error", 'error': user_form.errors})
        else:
            # Save the user, the account, and log in the new user
            user = user_form.save()
            address = request.POST['street'] , ", " + request.POST['city'] + ", " , request.POST['state'] , ", " + request.POST['zip_code']

            username = request.POST['username']
            password = request.POST['password1']

            if user is not None:
                login(request, user)

                profile = models.Profile(id=request.user, distance=35)
                profile.save()


                return render(request, "global/home.html", {})
            else:
                # There was an error authenticating the newly registered user.
                return render(request, "User/invalidLogin.html")
    # If just a GET request, then send them the html.
    return render(request, 'User/register.html', {'address_form':address_form, 'user_form': user_form})

def profile(request):
    return render(request, 'User/profile.html')
