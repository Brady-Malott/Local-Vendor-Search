import functools

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

bp = Blueprint('search', __name__)

@bp.route('/')
def index():
  return redirect(url_for('search.search'))

@bp.route('/search', methods=('GET', 'POST'))
def search():
  if request.method == 'POST':
    flash(request.form['search'])
    return redirect(url_for('search.info'))

  return render_template('search/search.html')

@bp.route('/info', methods=('GET', 'POST'))
def info():
  if request.method == 'POST':
    return

  return render_template('search/info.html')