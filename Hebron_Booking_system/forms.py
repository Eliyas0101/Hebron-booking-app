from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Email

class BookingForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    pickup_date = DateField('Pickup Date', validators=[DataRequired()])
    pickup_time = TimeField('Pickup Time', validators=[DataRequired()])
    pickup_street = StringField('Pickup Street', validators=[DataRequired()])
    pickup_city = StringField('Pickup City', validators=[DataRequired()])
    pickup_state = StringField('Pickup State', validators=[DataRequired()])
    pickup_zip = StringField('Pickup ZIP', validators=[DataRequired()])
    dropoff_street = StringField('Dropoff Street', validators=[DataRequired()])
    dropoff_city = StringField('Dropoff City', validators=[DataRequired()])
    dropoff_state = StringField('Dropoff State', validators=[DataRequired()])
    dropoff_zip = StringField('Dropoff ZIP', validators=[DataRequired()])

    submit = SubmitField('Submit')

