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
    vendors = get_vendors(request.form['distance'])
    return render_template('search/search.html', vendors=vendors)

  return render_template('search/search.html')

@bp.route('/info', methods=('GET', 'POST'))
def info(text):
  if request.method == 'POST':
    return

  return render_template('search/info.html')

def get_vendors(distance):
  # Make request to external api

  jsonResponse = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=42.041725972123416,-82.73100565945686&radius={distance}&key=AIzaSyAY0zWfgbZso6jkaj-ZLof79cj_NAyCk9k&type=meal_takeaway').json()

  results = jsonResponse['results']

  data = []

  for item in results:
    # Check if certain keys exist in the results

    # opening_hours
    if 'opening_hours' in item:
      isOpen = item['opening_hours']['open_now']
    else:
      isOpen = False

    # rating
    if 'rating' in item:
      rating = str(item['rating'])
    else:
      rating = 'No rating'
    
    place = {
      'name': item['name'],
      'address': item['vicinity'],
      'rating': rating,
      'open': isOpen
    }
    data.append(place)

  return data
