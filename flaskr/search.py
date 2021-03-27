import functools

from flask import (
    Blueprint, redirect, render_template, request, url_for
)

bp = Blueprint('search', __name__)

@bp.route('/')
def index():
  return render_template('search/index.html')