#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    website=db.Column(db.String(120))
    shows= db.relationship("Shows",backref="venues",cascade="all, delete")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    website=db.Column(db.String(120))
    shows= db.relationship("Shows", backref="artists",cascade="all, delete")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Shows(db.Model):

    __tablename__='shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id=db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id=db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time= db.Column('start_time',db.DateTime, nullable=False)
    
    
    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/', methods=['GET','POST','DELETE'])
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  curr_date=datetime.datetime.now()
  dataya=[]
  venues=Venue.query.all()
  locations=[]
  pastshows=[]
  futshows=[]
  #grouping venues byt city/state lcoation
  locations=db.session.query(Venue.state,Venue.city).distinct()
  for location in locations:
    location_v=[]
    location_data={"city":location[1],"state":location[0]}
    location_venues=Venue.query.filter(Venue.city==location[1],Venue.state==location[0])
    for venue in location_venues:
      shows=venue.shows
      for show in shows:
        if show.start_time<=curr_date:  
          pastshows.append(show)
        else:
          futshows.append(show)
      #for each venue get needed data according to data schema required
      venue_data={
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":len(futshows)
      }
      location_v.append(venue_data)
    location_data["venues"]=location_v
    dataya.append(location_data)  
  venues =Venue.query.all()
  data1=[]
  for venue in venues:
    data1.append({"id":venue.id,"name":venue.name})
    #print(data1)
  return render_template('pages/venues.html', areas=dataya);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form['search_term']
  results=Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all() 
  response={
    "count": len(results),
    "data": results
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  curr_date=datetime.datetime.now()
  venue=Venue.query.get(venue_id)
  pastshows=[]
  futshows=[]
  #SELECT DISTINCT "Venue".id AS "Venue_id", "Venue".name AS "Venue_name", 
  # "Venue".image_link AS "Venue_image_link", shows.start_time AS shows_start_time
  #FROM "Venue" JOIN shows ON "Venue".id = shows.venue_id JOIN "Artist" ON "Artist".id = shows.artist_id
  #WHERE "Artist".id = %(id_1)s
  shows=db.session.query(Artist.id,Artist.name,Artist.image_link,\
  Shows.start_time).join(Venue.shows).join(Shows.artists).filter(Venue.id==venue_id).distinct().all()
  #loop over venue shows and get needed info for each show
  for show in shows:
    show_data={
      "artist_id":show[0],
      "artist_name":show[1],
      "artist_image_link":show[2],
      "start_time":str(show[3])
      }
    if show[3]<=curr_date:  
      pastshows.append(show_data)
    else:
      futshows.append(show_data)
  #extract needed data from venue 
  datax={
      "id":venue.id,
      "name":venue.name,
      "genres":venue.genres.split(" "),
      "address":venue.address,
      "city":venue.city,
      "state":venue.state,
      "phone":venue.phone,
      "website":venue.website,
      "facebook_link":venue.facebook_link,
      "seeking_talent":venue.seeking_talent,
      "seeking_description":venue.seeking_description,
      "image_link":venue.image_link,
      "past_shows":pastshows,
      "upcoming_shows":futshows,
      "past_shows_count":len(pastshows),
      "upcoming_shows_count":len(futshows)
      }  
  return render_template('pages/show_venue.html', venue=datax)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
#check if seeking info is provided if not set it to False
    if("seeking_talent" in request.form.keys()):
      seeking=True
    else:
      seeking=False
    form=VenueForm(request.form)

  # TODO: insert form data as a new Venue record in the db, instead
    new_venue=Venue(name=request.form['name'],city=request.form['city'],
    state=request.form['state'],address=request.form['address'],
    phone=request.form['phone'],facebook_link=request.form['facebook_link'],
    genres= ' '.join(map(str, request.form.getlist('genres'))),seeking_talent=seeking,
    seeking_description=request.form["seeking_description"],website=request.form["website"],image_link=request.form['image_link'])
    #print(request.form.getlist('genres'))
    print(new_venue)
    try:
      db.session.add(new_venue)
      db.session.commit()
    
  # TODO: modify data to be the data object returned from db insertion
  

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      flash('An error occurred. Venue ' +request.form['name']+"could not be listed")
      db.session.rollback()
    else:
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #Venue.query.filter(Venue.id==venue_id).delete()
  venue=Venue.query.get(venue_id)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  db.session.delete(venue)
  try:
    db.session.commit()
  except:
    db.session.rollback()
    flash('Venue ' + Venue.query.get(venue_id)+ ' Couldnt be deleted')
  print(venue_id)
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #loop over artists and get needed info
  artists =Artist.query.all()
  data=[]
  for artist in artists:
    data.append({"id":artist.id,"name":artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #case insensitive search for artists
  search_term=request.form['search_term']
  results=Artist.query.filter(Artist.name.ilike("%"+search_term+"%")).all() 
  response={
    "count": len(results),
    "data": results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  curr_date=datetime.datetime.now()
  artist=Artist.query.get(artist_id)
  pastshows=[]
  futshows=[]
  #SELECT DISTINCT "Venue".id , "Venue".name , "Venue".image_link , shows.start_time 
  #FROM "Venue" JOIN shows ON "Venue".id = shows.venue_id JOIN "Artist" ON "Artist".id = shows.artist_id
  #WHERE "Artist".id =artist_id
  shows=db.session.query(Venue.id,Venue.name,Venue.image_link,Shows.start_time).join(Venue.shows).\
  join(Shows.artists).filter(Artist.id==artist_id).distinct().all()
  #loop over shows, compare start time with current time and append 2 arrays accordingly
  for show in shows:
    #venue_show=Venue.query.get(show.venue_id)
    show_data={
      "venue_id":show[0],
      "venue_name":show[1],
      "venue_image_link":show[2],
      "start_time":str(show[3])
      }
    if show.start_time<=curr_date:  
      pastshows.append(show_data)
    else:
      futshows.append(show_data)
  #this is the data passed in return statment
  dataz={
    "id":artist.id,
    "name":artist.name,
    "genres":artist.genres.split(" "),
    "city":artist.city,
    "state":artist.state,
    "phone":artist.phone,
    "website":artist.website,
    "facebook_link":artist.facebook_link,
    "seeking_venue":artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link":artist.image_link,
    "past_shows":pastshows,
    "upcoming_shows":futshows,
    "past_shows_count": len(pastshows),
    "upcoming_shows_count": len(futshows),
  }
  return render_template('pages/show_artist.html', artist=dataz)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = EditArtistForm()
  #get artist by id
  artistz=Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artistz)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #still
  decis={"y":True,"n":False}
  artist_edited=Artist.query.get(artist_id)
  print(request.form)
  #print(decis[request.form['seeking_venue']])
  if("".join(request.form['city'].split())):
      artist_edited.city=request.form['city']
  if("".join(request.form['state'].split())):   
      artist_edited.state=request.form['state']
  if("".join(request.form['phone'].split())):
      artist_edited.phone=request.form['phone']
  if("genres" in request.form.keys()):
       artist_edited.genres= ' '.join(map(str, request.form.getlist('genres')))
  if("".join(request.form['facebook_link'].split())):
      artist_edited.facebook_link=request.form['facebook_link']
  if("".join(request.form['website'].split())):
      artist_edited.website=request.form['website']
  if('seeking_venue' in request.form.keys()):
       artist_edited.seeking_venue=decis[request.form['seeking_venue']]
       if("".join(request.form['seeking_description'].split())):
            artist_edited.seeking_description=request.form['seeking_description']
  else:
    artist_edited.seeking_venue=False
  # on successful db insert, flash success
  try:
    db.session.commit()
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('Artist ' + artist_edited.name + ' was NOT successfully edited')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    flash('Artist ' + artist_edited.name + ' was successfully edited')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = EditVenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  decis={"y":True,"n":False}
  venue_edited=Venue.query.get(venue_id)
  print(request.form)
  #print(decis[request.form['seeking_venue']])
  if("".join(request.form['city'].split())):
      venue_edited.city=request.form['city']
  if("".join(request.form['state'].split())):   
      venue_edited.state=request.form['state']
  if("".join(request.form['phone'].split())):
      venue_edited.phone=request.form['phone']
  if("".join(request.form['address'].split())):
      venue_edited.phone=request.form['address']
  if("genres" in request.form.keys()):
       venue_edited.genres= ' '.join(map(str, request.form.getlist('genres')))
  if("".join(request.form['facebook_link'].split())):
      venue_edited.facebook_link=request.form['facebook_link']
  if("".join(request.form['website'].split())):
      venue_edited.website=request.form['website']
  if('seeking_talent' in request.form.keys()):
       venue_edited.seeking_talent=decis[request.form['seeking_talent']]
       if("".join(request.form['seeking_description'].split())):
            venue_edited.seeking_description=request.form['seeking_description']
  else:
    venue_edited.seeking_talent=False
  # on successful db insert, flash success
  try:
    db.session.commit()
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('Venue ' + venue_edited.name + ' was NOT successfully edited')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    flash('Venue ' + venue_edited.name + ' was successfully edited')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form=ArtistForm(request.form)
  print("validation result: "+str(form.validate_on_submit()))
  if("seeking_venue" in request.form.keys()):
    seeking=True
  else:
    seeking=False
  print(seeking)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  new_artist=Artist(name=request.form['name'], city=request.form['city'],
  state=request.form['state'], phone=request.form['phone'],genres= ' '.join(map(str, request.form.getlist('genres'))),
  facebook_link=request.form['facebook_link'],seeking_venue=seeking,
  seeking_description=request.form["seeking_description"],website=request.form["website"],image_link=request.form['image_link'])
  # on successful db insert, flash success
  print(new_artist)
  try:
    db.session.add(new_artist)
    db.session.commit()
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  showz=Shows.query.all()
  for show in showz:
    data1={
    "venue_id":show.venues.id,
    "venue_name":show.venues.name,
    "artist_id":show.artists.id,
    "artist_name":show.artists.name,
    "artist_image_link":show.artists.image_link,
    "start_time":str(show.start_time)}
    data.append(data1)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artistid=request.form["artist_id"]
  venueid=request.form["venue_id"]
  date=request.form["start_time"]

  print("artistid :"+artistid+"venueid: "+venueid+ "date: "+date)
  show=Shows(artist_id=artistid,venue_id=venueid,start_time=date)
  db.session.add(show)
  try:
    db.session.commit()
  except:
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')
 
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
