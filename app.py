#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  venues = Venue.query.all()

  for place in Venue.query.distinct(Venue.city, Venue.state).all():
    data.append({
      'city': place.city,
      'state': place.state,
      'venues': [{
          'id': venue.id,
          'name': venue.name,
      } for venue in venues if
          venue.city == place.city and venue.state == place.state]
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '').strip()
  data = []
  curret_data_time = datetime.now()
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  for venue in venues:
    nshows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > str(curret_data_time)).all()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(nshows)
    })

  response = {
      "count": len(venues),
      "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  pshows = []
  ushows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  curret_data_time = datetime.now()
  venue = Venue.query.get(venue_id)
  vpshows = db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time < str(curret_data_time)).all()
  vushows = db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time > str(curret_data_time)).all()

  for vpshow in vpshows:
    past_shows_count=+1
    pshows.append({
      "artist_id": vpshow.artist_id,
      "artist_name": db.session.query(Artist.name).filter_by(id=vpshow.artist_id).all(),
      "artist_image_link": db.session.query(Artist.image_link).filter_by(id=vpshow.artist_id).all(),
      "start_time": str(vpshow.start_time)
    })

  for vushow in vushows:
    upcoming_shows_count = +1
    ushows.append({
      "artist_id": vushow.artist_id,
      "artist_name": db.session.query(Artist.name).filter_by(id=vushow.artist_id).all(),
      "artist_image_link": db.session.query(Artist.image_link).filter_by(id=vushow.artist_id).all(),
      "start_time": str(vushow.start_time)
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pshows,
    "upcoming_shows": ushows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False
  form = VenueForm(request.form)

  try:
    new_venue = Venue(
      name=request.form.data,
      city=request.form.data,
      state=request.form.data,
      address=request.form.data,
      phone=request.form.data,
      website=request.form.data,
      seeking_talent=request.form.data,
      image_link=request.form.data,
      genres=request.form.data,
      facebook_link=request.form.data,
      seeking_description=request.form.data
      )
    form.populate_obj(new_venue)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
       # on unsuccessful db insert, flash an error.
      flash('An error occurred. Venue could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return url_for('venues', venue_id=venue_id)

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():

  data = []
  artists = Artist.query.all()

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '').strip()
  data = []
  curret_data_time = datetime.now()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  for artist in artists:
    nshows = db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > str(curret_data_time)).all()
    data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(nshows)
    })

  response = {
      "count": len(artists),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm()

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False

  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name'),
    artist.city = request.form.get('city'),
    artist.state = request.form.get('state'),
    artist.phone = request.form.get('phone'),
    artist.website = request.form.get('website'),
    artist.seeking_venue = request.form.get('seeking_venue'),
    artist.image_link = request.form.get('image_link'),
    artist.genres = request.form.get('genres'),
    artist.facebook_link = request.form.get('facebook_link'),
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db update, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
       # on unsuccessful db update, flash an error.
      flash('An error occurred.Artist could not be updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)
  form = VenueForm()

  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name'),
    venue.city = request.form.get('city'),
    venue.state = request.form.get('state'),
    venue.address = request.form.get('address'),
    venue.phone = request.form.get('phone'),
    venue.website=request.form.get('website'),
    venue.seeking_talent=request.form.get('seeking_talent'),
    venue.image_link = request.form.get('image_link'),
    venue.genres = request.form.get('genres'),
    venue.facebook_link = request.form.get('facebook_link'),
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db update, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
       # on unsuccessful db update, flash an error.
      flash('An error occurred.Venue could not be updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  form = ArtistForm(request.form)

  try:
    new_artist = Artist(
      name=request.form.data, 
      city=request.form.data, 
      state=request.form.data, 
      phone=request.form.data,
      website=request.form.data,
      seeking_venue=request.form.data,
      image_link=request.form.data,
      genres=request.form.data,
      facebook_link=request.form.data,
      seeking_description=request.form.data
      )
    form.populate_obj(new_artist)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
       # on unsuccessful db insert, flash an error.
      flash('An error occurred. Artist could not be listed.')

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  shows = Show.query.all()

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": db.session.query(Venue.name).filter_by(id=show.venue_id).all(),
      "artist_id": show.artist_id,
      "artist_name": db.session.query(Artist.name).filter_by(id=show.artist_id).all(),
      "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.artist_id).all(),
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():

  form = ShowForm()

  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False
  form = ShowForm()
  
  try:
    new_show = Show(
      artist_id=request.form.data,
      venue_id=request.form.data,
      start_time=request.form.data,
    )
    form.populate_obj(new_show)
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
       # on unsuccessful db insert, flash an error.
      flash('An error occurred. Show could not be listed.')
      
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
