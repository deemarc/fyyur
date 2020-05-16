#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort,jsonify,current_app
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler
from forms import *
from config import Config
from flask_migrate import Migrate


from database import db
from database.models import *
# from database.shemas import VenueSchema
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.Config')
db.init_app(app)
migrate = Migrate(app,db)


# DONE: connect to a local postgresql database


def flash_errors(form):
    """Flashes form errors"""
    error = False
    for field, errors in form.errors.items():
      if not request.form[field]:
        # for non-require empty field we don't have to throw error
        continue
      error = True
      for error in errors:
          flash(u"Error in the %s field - %s" % (
              getattr(form, field).label.text,
              error
          ), 'error')
    return error


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Schema init
#----------------------------------------------------------------------------#
# venue_schema = VenueSchema()
# venues_schema = VenueSchema(many=True)


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
@app.route('/index')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "venues": [{
  #       "id": 1,
  #       "name": "The Musical Hop",
  #       "num_upcoming_shows": 0,
  #     }, {
  #       "id": 3,
  #       "name": "Park Square Live Music & Coffee",
  #       "num_upcoming_shows": 1,
  #     }]
  #   }, {
  #     "city": "New York",
  #     "state": "NY",
  #     "venues": [{
  #       "id": 2,
  #       "name": "The Dueling Pianos Bar",
  #       "num_upcoming_shows": 0,
  #     }]
  #   }]
  
  venues = Venue.query.order_by(Venue.state, Venue.city).all()
  raw_data = {}
  
  # raw_data[states][city]
  for venue in venues:
    cur_state = venue.state
    cur_city = venue.city
    if cur_state not in raw_data:
      raw_data[cur_state] = {}

    if cur_city not in raw_data[cur_state]:
      raw_data[cur_state][cur_city] =[]
    
    raw_data[cur_state][cur_city].append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_show": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > db.func.current_timestamp()).count()
    })
    current_app.logger.debug(f"venus raw_data item:{raw_data}")

  data_list = []

  for cur_state in raw_data:
    for cur_city in raw_data[cur_state]:
      data_list.append({
        "city": cur_city,
        "state": cur_state,
        "venues": raw_data[cur_state][cur_city]
      })
    
  return render_template('pages/venues.html', areas=data_list)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # result = db.table.filter(db.table.column.ilike(looking_for))
  # inStr = request.form['search']
  inStr = request.form.get('search_term', '')
  looking_for = f"%{inStr}%"
  # print(f"looking for: {looking_for}")
  venues = Venue.query.filter(Venue.name.ilike(looking_for))
  response = {}
  response['count'] = venues.count()
  data = []
  for venue in venues:
    item = {
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":venue.num_shows
    }
    data.append(item)
  response["data"] = data


  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    if not venue:
      abort(404,f"Venue with venue_id:{venue_id} cannot be found")
    venue_data = venue.dump()
    venue_data.update(venue.dump_shows())
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False   
  form = VenueForm()
  if not form.validate_on_submit():
    if flash_errors(form):
      return render_template('forms/new_venue.html', form=form)
  
  try:
    venue_name = request.form['name']
    data = {}
    data['name']=request.form['name']
    data['genres']=request.form.getlist('genres')
    data['address']=request.form['address']
    data['city']=request.form['city']
    data['state']=request.form['state']
    data['phone']=request.form['phone']
    data['website']=request.form['website']
    data['facebook_link']=request.form['facebook_link']
    data['image_link']=request.form['image_link']
    data['seeking_talent']= bool(request.form.get('seeking_talent',False))
    data['description']=request.form['seeking_description']
    new_venue = Venue(**data)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
   # DONE: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
    return abort(500,errMsg)


  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
 
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    if not venue:
      abort(404,f"Venue with venue_id:{venue_id} cannot be found")
    venue_name = venue.name
    result = Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    print(f"delete done, delete result={result}")
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  if error:
    abort(500,errMsg)
  else:
    flash(f"Venue id:{venue_id}, name:{venue_name} is successfully deleted")    
    return jsonify({'success':True})


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  abort(500,errMsg)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  artists = Artist.query.order_by(Artist.id).all()
  data = []
  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  inStr = request.form.get('search_term', '')
  looking_for = f"%{inStr}%"

  artists = Artist.query.filter(Artist.name.ilike(looking_for))
  response = {}
  response['count'] = artists.count()
  data = []
  for artist in artists:
    item = {
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows":artist.num_shows 
      # "num_upcoming_shows":artist.num_shows
    }
    data.append(item)
  response["data"] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    if not artist:
      abort(404,f"Artist with artist_id:{artist_id} cannot be found")
    artist_data = artist.dump()
    artist_data.update(artist.dump_shows())
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)


  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  error = False
  try:
    artistObj = Artist.query.filter_by(id=artist_id).first()
    if not artistObj:
      abort(404,f"Artist with artist_id:{artist_id} cannot be found")
    artist = artistObj.dump()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)
    
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artistObj = Artist.query.filter_by(id=artist_id).first()
    if not artistObj:
      abort(404,f"Artist with artist_id:{artist_id} cannot be found")
    for key, value in request.form.items():
      setattr(artistObj, key, value)
    db.session.add(artistObj)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  error = False
  try:
    venueObj = Venue.query.filter_by(id=venue_id).first()
    if not venueObj:
      abort(404,f"Venue with venue_id:{venue_id} cannot be found")
    venue = venueObj.dump()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venueObj = Venue.query.filter_by(id=venue_id).first()
    if not venueObj:
      abort(404,f"Venue with venue_id:{venue_id} cannot be found")
    
    for key, value in request.form.items():
      setattr(venueObj, key, value)
    db.session.add(artistObj)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    abort(500,errMsg)
    

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion

  error = False   
  form = ArtistForm()
  if not form.validate_on_submit():
    if flash_errors(form):
      return render_template('forms/new_artist.html', form=form)
  try:
    artist_name = request.form['name']
    data = {}
    data['name']=request.form['name']
    data['genres']=request.form.getlist('genres')
    data['city']=request.form['city']
    data['state']=request.form['state']
    data['phone']=request.form['phone']
    data['website']=request.form['website']
    data['facebook_link']=request.form['facebook_link']
    data['image_link']=request.form['image_link']
    data['seeking_venue']= bool(request.form.get('seeking_venue',False))
    data['seeking_description']=request.form['seeking_description']
    new_artist = Artist(**data)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + artist_name + ' could not be listed.')
    return abort(500,errMsg)

  # on successful db insert, flash success
  flash('Artist ' + artist_name + ' was successfully listed!')
  # Done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = []
  for show in shows:
    data.append(show.dump())


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False   
  form = ShowForm()
  if not form.validate_on_submit():
    if flash_errors(form):
      return render_template('forms/new_show.html', form=form)

  new_show = Show()
  try:
    for key, value in request.form.items():
      # just to make sure the user didn't try to insert new id be themselves
      if key != 'id':
        app.logger.debug(f"key:{key}")
        setattr(new_show, key, value)
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    errMsg = sys.exc_info()
  finally:
    db.session.close()

  # shows don't really have name or anything to identified so we just say something
  if error:
    flash('An error occurred. The provided infomation about the show could not be listed.')
    return abort(500,errMsg)

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
