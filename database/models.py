from . import db
from sqlalchemy_utils import aggregated
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
    description = db.Column(db.String(1024), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[])
    shows =db.relationship('Show', backref='Venue', lazy='dynamic')

    @aggregated('shows', db.Column(db.Integer,default=0))
    def num_shows(self):
        return db.func.count('1')

    def dump(self):
        if not self.genres:
            genres = []
        else:
            genres = self.genres

        if not self.num_shows:
            num_shows = 0
        else:
            num_shows = self.num_shows

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
            'description' :self.description,
            'image-link' :self.image_link,
            'num_shows' : num_shows
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
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
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
            'image-link' :self.image_link,
        }
        

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

