import functools
import requests

from flask import (
    Blueprint, flash, session, redirect, render_template, request, url_for
)

bp = Blueprint('searchBP', __name__)

@bp.route('/')
def index():
  return redirect(url_for('searchBP.location'))

@bp.route('/search', methods=('GET', 'POST'))
def search(vendors=None):
  if request.method == 'POST':
    vendors = get_vendors(request.form)
    return render_template('search/search.html', vendors=vendors)

  return render_template('search/search.html')

@bp.route('/location', methods=('GET', 'POST'))
def location():
  if request.method == 'POST':
    location = get_location(request.form['location'])
    return redirect(url_for('searchBP.search'))
  
  return render_template('search/location.html')
    

@bp.route('/info', methods=['POST'])
def info():
  import json

  vendor = eval(request.form['info-btn'])
  
  if vendor['photo_reference'] != None:
    create_static_image(vendor['photo_reference'])
  
  delivery_class = 'fas fa-check' if vendor['delivery'] else 'fas fa-times'
  takeout_class = 'fas fa-check' if vendor['takeout'] else 'fas fa-times'
  
  vendor['delivery'] = delivery_class
  vendor['takeout'] = takeout_class

  return render_template('search/info.html', vendor=vendor)

def get_vendors(form):

  # Get search distance and filters
  distance = form['distance']
  type_string = 'meal_delivery' if 'delivery' in form.keys() else 'meal_takeaway'

  # Make request to external api
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={session["lat"]},{session["lng"]}&radius={distance}&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k&type={type_string}').json()
  results = json_response['results']

  data = []
  for item in results:
    # Check if certain keys exist in the results

    # opening_hours
    if 'opening_hours' in item:
      is_open = item['opening_hours']['open_now']
    else:
      is_open = False

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
    }
    data.append(place)

  return data

def get_location(location):

  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k').json()

  place_id = json_response['candidates'][0]['place_id']
  
  json_response = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k&place_id={place_id}&fields=geometry').json()

  location = json_response['result']['geometry']['location']

  session['lat'] = location['lat']
  session['lng'] = location['lng']

def create_static_image(photo_reference):
  import os

  static_directory = 'flaskr/static/'
  for filename in os.listdir(static_directory):
    if filename.endswith('.jpg'):
      os.remove(static_directory + filename)

  raw_image_data = requests.get(f'https://maps.googleapis.com/maps/api/place/photo?photoreference={photo_reference}&maxwidth=600&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k')

  f = open(f'flaskr/static/{photo_reference}.jpg', 'wb')

  for chunk in raw_image_data:
    if chunk:
      f.write(chunk)

  f.close()
