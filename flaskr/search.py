import functools
import requests

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

bp = Blueprint('searchBP', __name__)

@bp.route('/')
def index():
  return redirect(url_for('searchBP.search'))

@bp.route('/search', methods=('GET', 'POST'))
def search(vendors=None):
  if request.method == 'POST':
    vendors = get_vendors(request.form)
    return render_template('search/search.html', vendors=vendors)

  return render_template('search/search.html')

#@bp.route('/location', methods=('GET', 'POST'))
#def location();
 # if request.method == 'POST':
   # location = get_location(request.form)
    #return render_template('search/search.html', location=location)
  
 # return render_template('search/location.html')
    





@bp.route('/info', methods=['POST'])
def info():
  import json

  vendor = eval(request.form['info-btn'])
  
  if vendor['photo_reference'] != None:
    img_src = get_img_src(vendor['photo_reference'])
    vendor['photo_reference'] = img_src

  return render_template('search/info.html', vendor=vendor)

def get_vendors(form):

  # Get search distance and filters
  distance = form['distance']
  type_string = 'meal_delivery' if 'delivery' in form.keys() else 'meal_takeaway'

  # Make request to external api
  jsonResponse = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=42.041725972123416,-82.73100565945686&radius={distance}&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k&type={type_string}').json()

  results = jsonResponse['results']

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
    
    place = {
      'name': item['name'],
      'address': item['vicinity'],
      'rating': rating,
      'open': is_open,
      'photo_reference': photo_reference,
    }
    data.append(place)

  return data

#def get_location(form):

def get_img_src(photo_reference):
  return requests.get(f'https://maps.googleapis.com/maps/api/place/photo?photoreference={photo_reference}&maxwidth=600&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k')
