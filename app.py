#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from flask_migrate import Migrate
import sys
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format)

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
  venues = Venue.query.order_by(Venue.state).all()

  for venue in venues:
    venueCollection = {
      'id': venue.id,
      'name': venue.name,
    }

    if len(data) > 0:
      previous = data[len(data) - 1]

      if previous['city'] == venue.city and previous['state'] == venue.state:
        previous['venues'].append(venueCollection)
        continue

    data.append({
      'city': venue.city,
      'state': venue.state,
      'venues': [venueCollection] 
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.like(search)).all()
  response={
    "count": len(venues),
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  
  return render_template('pages/show_venue.html', venue=venue.json())

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = None

  # try:
  #   data = request.get_json()
  #   data['seeking_talent'] = True if data['seeking_talent'] == 'True' else False
  #   venue = Venue(**data)
  #   db.session.add(venue)
  #   db.session.commit()
  #   venue_id = venue.id
    
  # except:
  #   db.session.rollback()
  #   error = 'Invalid data'
  #   print(sys.exc_info())

  try:
    form = VenueForm(request.form)
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue: {0} created successfully'.format(venue.name))
  except Exception as err:
    flash('An error occurred creating the Venue: {0}. Error: {1}'.format(venue.name, err))
    db.session.rollback()

  finally:
    db.session.close()

  # if error:
  #   flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  #   abort(500)
  # else:
  #   flash('Venue ' + data['name'] + ' was successfully listed!')
  #   return redirect(url_for('show_venue', venue_id = venue_id))

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  error = None

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    abort(500)
  else:
    flash('Venue ' + venue_id + ' was successfully deleted!')
    return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(
    name = venue.name,
    address = venue.address,
    city = venue.city,
    state = venue.state,
    genres = json.loads(venue.genres),
    phone = venue.phone,
    image_link = venue.image_link,
    facebook_link = venue.facebook_link,
    website = venue.website,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description,
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = None

  try:
    data = request.get_json()
    data['seeking_talent'] = True if data['seeking_talent'] == 'True' else False
    db.session.query(Venue).filter(Venue.id == venue_id).update(data, synchronize_session=False)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + data['name'] + ' could not be updated.')
    abort(500)
  else:
    flash('Venue ' + data['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  artists = Artist.query.filter(Artist.name.like(search)).all()
  response={
    "count": len(artists),
    "data": artists
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  return render_template('pages/show_artist.html', artist=artist.json())

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    name = artist.name,
    city = artist.city,
    state = artist.state,
    genres = json.loads(artist.genres),
    phone = artist.phone,
    image_link = artist.image_link,
    facebook_link = artist.facebook_link,
    website = artist.website,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description,
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = None

  try:
    data = request.get_json()
    data['seeking_venue'] = True if data['seeking_venue'] == 'True' else False
    db.session.query(Artist).filter(Artist.id == artist_id).update(data, synchronize_session=False)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + data['name'] + ' could not be updated.')
    abort(500)
  else:
    flash('Artist ' + data['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = None

  try:
    data = request.get_json()
    data['seeking_venue'] = True if data['seeking_venue'] == 'True' else False
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit()
    artist_id = artist.id
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
    abort(500)
  else:
    flash('Artist ' + data['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  error = None

  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + artist_id + ' could not be deleted.')
    abort(500)
  else:
    flash('Artist ' + artist_id + ' was successfully deleted!')
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()

  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = None

  try:
    data = request.get_json()
    show = Show(**data)
    db.session.add(show)
    db.session.commit()
    
  except:
    db.session.rollback()
    error = 'Invalid data'
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.')
    abort(500)
  else:
    flash('Show was successfully listed!')
    return redirect(url_for('index'))
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
