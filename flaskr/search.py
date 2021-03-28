import requests

from flask import (
    Blueprint, flash, session, redirect, render_template, request, url_for
)

from config import Config

bp = Blueprint('searchBP', __name__)

@bp.route('/')
def index():
  return redirect(url_for('searchBP.location'))

@bp.route('/location', methods=('GET', 'POST'))
def location():
  if request.method == 'POST':
    location = get_location(request.form['location'])
    return redirect(url_for('searchBP.search'))
  
  return render_template('search/location.html')

@bp.route('/search', methods=('GET', 'POST'))
def search(vendors=None):
  if request.method == 'POST':
    vendors = get_vendors(request.form)
    return render_template('search/search.html', vendors=vendors)

  return render_template('search/search.html')
    
@bp.route('/search-nearby', methods=['POST'])
def search_nearby():
  vendors = get_nearby_vendors()
  return render_template('search/search.html', vendors=vendors)

@bp.route('/info', methods=['POST'])
def info():
  import json

  vendor = eval(request.form['info-btn'])
  
  if vendor['photo_reference'] != None:
    create_static_image(vendor['photo_reference'])

  get_vendor_details(vendor)

  return render_template('search/info.html', vendor=vendor)

def get_vendors(form):

  # Get search distance and filters
  distance = form['distance']
  type_string = 'meal_delivery' if form['filter'] == 'delivery' else 'meal_takeaway'
  key = Config.API_KEY

  # Make request to external api
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={session["lat"]},{session["lng"]}&key={key}&type={type_string}&radius={distance}').json()
  results = json_response['results']

  data = []
  for item in results:
    # Check if certain keys exist in the results

    # opening_hours
    if 'opening_hours' in item:
      is_open = item['opening_hours']['open_now']
    else:
      is_open = False

    is_open = 'Open' if is_open else 'Closed'

    # rating
    if 'rating' in item:
      rating = str(item['rating'])
    else:
      rating = 'No rating'

    # Photo reference
    if 'photos' in item:
      photo_reference = item['photos'][0]['photo_reference']
    else:
      photo_reference = None

    # Add types if they exist
    delivery = False
    takeout = False
    if 'types' in item:
      types = item['types']
      delivery = 'meal_delivery' in types
      takeout = 'meal_takeaway' in types
    
    place = {
      'name': item['name'],
      'address': item['vicinity'],
      'rating': rating,
      'open': is_open,
      'photo_reference': photo_reference,
      'delivery': delivery,
      'takeout': takeout,
      'place_id': item['place_id']
    }
    data.append(place)

  return data

def get_nearby_vendors():

  # Make request to external api
  key = Config.API_KEY
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={session["lat"]},{session["lng"]}&key={key}&type=meal_takeaway&rankby=distance').json()
  results = json_response['results']

  data = []
  for item in results:
    # Check if certain keys exist in the results

    # opening_hours
    if 'opening_hours' in item:
      is_open = item['opening_hours']['open_now']
    else:
      is_open = False

    is_open = 'Open' if is_open else 'Closed'

    # rating
    if 'rating' in item:
      rating = str(item['rating'])
    else:
      rating = 'No rating'

    # Photo reference
    if 'photos' in item:
      photo_reference = item['photos'][0]['photo_reference']
    else:
      photo_reference = None

    # Add types if they exist
    delivery = False
    takeout = False
    if 'types' in item:
      types = item['types']
      delivery = 'meal_delivery' in types
      takeout = 'meal_takeaway' in types
    
    place = {
      'name': item['name'],
      'address': item['vicinity'],
      'rating': rating,
      'open': is_open,
      'photo_reference': photo_reference,
      'delivery': delivery,
      'takeout': takeout,
      'place_id': item['place_id']
    }
    data.append(place)

  return data

def get_location(location):

  key = Config.API_KEY
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&key={key}').json()

  place_id = json_response['candidates'][0]['place_id']
  
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?key={key}&place_id={place_id}&fields=geometry').json()

  location = json_response['result']['geometry']['location']

  session['lat'] = location['lat']
  session['lng'] = location['lng']

def create_static_image(photo_reference):
  import os

  static_directory = 'flaskr/static/'
  for filename in os.listdir(static_directory):
    if filename.endswith('.jpg'):
      os.remove(static_directory + filename)

  key = Config.API_KEY
  raw_image_data = requests.get(f'https://maps.googleapis.com/maps/api/place/photo?photoreference={photo_reference}&maxwidth=600&key={key}')

  f = open(f'flaskr/static/{photo_reference}.jpg', 'wb')

  for chunk in raw_image_data:
    if chunk:
      f.write(chunk)

  f.close()

def get_vendor_details(vendor):
  delivery_class = 'fas fa-check' if vendor['delivery'] else 'fas fa-times'
  takeout_class = 'fas fa-check' if vendor['takeout'] else 'fas fa-times'
  
  vendor['delivery'] = delivery_class
  vendor['takeout'] = takeout_class

  key = Config.API_KEY
  details_response = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?key={key}&place_id={vendor["place_id"]}&fields=opening_hours,website,formatted_phone_number').json()['result']

  if 'opening_hours' in details_response:
    weekday_text = details_response['opening_hours']['weekday_text']
    vendor['opening_hours'] = get_opening_hours(weekday_text)
  else:
    vendor['opening_hours'] = ['Operating hours unavailable']
  
  if 'website' in details_response:
    vendor['website'] = details_response['website']
  else:
    vendor['website'] = '#'

  if 'formatted_phone_number' in details_response:
    vendor['phone_number'] = details_response['formatted_phone_number']
  else:
    vendor['phone_number'] = 'Phone number unavailable'

def get_opening_hours(weekday_text):

  opening_hours = []

  weekday_text.append(": 11-11")
  consecutive_days_Bool= False 
  consecutive_days_str = ""
  for i in range(len(weekday_text)-1):
    currentDay = weekday_text[i].split(": ") 
    nextDay = weekday_text[i+1].split(": ")
    if currentDay[1]==nextDay[1]:
      if not consecutive_days_Bool:
        consecutive_days_Bool = True
        consecutive_days_str = currentDay[0]
    else:
      if consecutive_days_Bool:
        consecutive_days_Bool = False          
        consecutive_days_str = consecutive_days_str + "-" + currentDay[0] + " " + currentDay[1]
        opening_hours.append(consecutive_days_str)
        consecutive_days_str = ""
      else:
        opening_hours.append(currentDay[0] + " " + currentDay[1])
  return opening_hours