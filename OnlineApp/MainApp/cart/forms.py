from flask_wtf import FlaskForm
from wtforms import IntegerField


class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = IntegerField('ID')
