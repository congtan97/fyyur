from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    # show = db.relationship("Show", backref="venue_shows", cascade="all, delete", lazy='dynamic')

    def __repr__(self):
      return f'<Venue id: {self.id}, name: {self.name}>'

    def json(self):
      upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
      past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'genres':  json.loads(self.genres),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'upcoming_shows_count': len(upcoming_shows),
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'past_shows': past_shows,
      }

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    show = db.relationship("Show", backref="artist_shows", cascade="all, delete", lazy='dynamic')

    def __repr__(self):
      return f'<Artist id: {self.id}, name: {self.name}>'

    def json(self):
      upcoming_shows = self.show.filter(Show.start_time > datetime.now()).all()
      past_shows = self.show.filter(Show.start_time < datetime.now()).all()

      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': json.loads(self.genres),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'upcoming_shows_count': len(upcoming_shows),
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'past_shows': past_shows,
      }

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete="CASCADE"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship("Artist", backref="show_artists", lazy=True)
  venue = db.relationship("Venue", backref="show_venues", lazy=True)

  def __repr__(self):
    return f'<Show id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id} start_time: {self.start_time}>'