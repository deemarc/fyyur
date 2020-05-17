from . import db
from sqlalchemy_utils import aggregated
from sqlalchemy.ext.associationproxy import association_proxy
import datetime
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
    
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(1024), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[])
    shows =db.relationship('Show', backref='Venue', lazy='dynamic', cascade="save-update, merge, delete")


    def dump(self):
        if not self.genres:
            genres = []
        else:
            genres = self.genres

        return{
            'id' :self.id,
            'name' :self.name,
            'genres' : genres,
            'address' :self.address,
            'city' :self.city,
            'phone' :self.phone,
            'website' :self.website,
            'facebook_link':self.facebook_link,
            'seeking_talent' :self.seeking_talent,
            'seeking_description' :self.seeking_description,
            'image_link' :self.image_link
        }

    def dump_shows(self):
        upQ = Show.query.filter_by(venue_id=self.id).filter(Show.start_time > db.func.current_timestamp())
        passQ = Show.query.filter_by(venue_id=self.id).filter(Show.start_time <= db.func.current_timestamp())
        upcoming_shows_count = upQ.count()
        past_shows_count = passQ.count()
        upcoming_shows = list(map(Show.dump_artist_detail,upQ))
        past_shows = list(map(Show.dump_artist_detail,passQ))

        return {
            "upcoming_shows_count":upcoming_shows_count,
            "upcoming_shows":upcoming_shows,
            "past_shows_count":past_shows_count,
            "past_shows":past_shows
        }

    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1024), default=' ')
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True, cascade="save-update, merge, delete")
    
    def dump(self):
        
        if not self.genres:
            genres = []
        else:
            genres = self.genres        

        return {
            'id' :self.id,
            'name' :self.name,
            'genres' : genres,
            'city' :self.city,
            'phone' :self.phone,
            'website' :self.website,
            'facebook_link':self.facebook_link,
            'seeking_venue' :self.seeking_venue,
            'seeking_description' :self.seeking_description,
            'image_link' :self.image_link,
        }

    def dump_shows(self):
        upQ = Show.query.filter_by(artist_id=self.id).filter(Show.start_time > db.func.current_timestamp())
        passQ = Show.query.filter_by(artist_id=self.id).filter(Show.start_time <= db.func.current_timestamp())
        upcoming_shows_count = upQ.count()
        past_shows_count = passQ.count()
        upcoming_shows = list(map(Show.dump_venue_detail,upQ))
        past_shows = list(map(Show.dump_venue_detail,passQ))

        return {

            "upcoming_shows_count":upcoming_shows_count,
            "upcoming_shows":upcoming_shows,
            "past_shows_count":past_shows_count,
            "past_shows":past_shows
        }
    
        

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id, ondelete='cascade'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id, ondelete='cascade'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)

    # venue_name = association_proxy('venue_id', 'name',creator=lambda value: Venue.get(value))
    # artist_name = association_proxy('artist_id', 'name',creator=lambda value: Artist.get(value))
    def basic_info(self):
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        start_time = self.start_time.strftime(date_format)
        return {
            'id':self.id,
            'start_time':start_time
        }
    def dump(self):
        data = {
            'venue_id':self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id':self.artist_id,
            'artist_name':self.Artist.name
        }
        data.update(self.basic_info())
        return data

    def dump_artist_detail(self):
        data = {
            'artist_id':self.artist_id,
            'artist_name':self.Artist.name,
            'artist_image_link':self.Artist.image_link
        }
        data.update(self.basic_info())
        return data

    def dump_venue_detail(self):
        data = {
            'venue_id':self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link':self.Venue.image_link,
        }
        data.update(self.basic_info())
        return data
            
# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

