from marshmallow import EXCLUDE
from . import ma
from database.models import Venue

class VenueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Venue
        unknown = EXCLUDE