from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import urllib
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure SQL Server database connection
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-ECQTH0V\\SQLEXPRESS;DATABASE=HebronDB;Trusted_Connection=yes;")
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect={}".format(params)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Clients table model
class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(50))
    company_name = db.Column(db.String(100))  # Add this line
    trips = db.relationship('Trip', back_populates='client', lazy=True, cascade="all, delete-orphan")

# Trips table model
class Trip(db.Model):
    trip_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))
    pickup_datetime = db.Column(db.DateTime)  # Updated column
    pickup_street = db.Column(db.String(255))
    pickup_city = db.Column(db.String(50))
    pickup_state = db.Column(db.String(50))
    pickup_zip = db.Column(db.String(20))
    dropoff_street = db.Column(db.String(255))
    dropoff_city = db.Column(db.String(50))
    dropoff_state = db.Column(db.String(50))
    dropoff_zip = db.Column(db.String(20))
    fare = db.Column(db.Numeric(7, 2))
    invoices = db.relationship('Invoice', back_populates='trip', lazy=True)
    client = db.relationship('Client', back_populates='trips')  # Added this line

# Invoices table model
class Invoice(db.Model):
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.trip_id'), unique=True)
    invoice_date = db.Column(db.Date)
    booking_date = db.Column(db.Date, default=datetime.now().date())  # New column with a default value
    total_amount = db.Column(db.Numeric(7, 2))
    trip = db.relationship('Trip', back_populates='invoices')

# Home route
@app.route('/')
def home():
    # Clear the session data when accessing the homepage
    session.clear()
    return render_template('index.html')

# Booking route
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        # Retrieve form data
        client_first_name = request.form['first_name']
        client_last_name = request.form['last_name']
        client_email = request.form['email']
        client_phone_number = str(request.form['phone_number'])
        # Use company_name from the form if present, else None
        client_company_name = request.form['company_name'] if 'company_name' in request.form and request.form['company_name'] else None
        print(f"Company Name: {client_company_name}")
        pickup_datetime_str = request.form['pickup_datetime']
        pickup_street = request.form['pickup_street']
        pickup_city = request.form['pickup_city']
        pickup_state = request.form['pickup_state']
        pickup_zip = request.form['pickup_zip']
        dropoff_street = request.form['dropoff_street']
        dropoff_city = request.form['dropoff_city']
        dropoff_state = request.form['dropoff_state']
        dropoff_zip = request.form['dropoff_zip']

        # Store form data in session
        session['client_first_name'] = client_first_name
        session['client_last_name'] = client_last_name
        session['client_email'] = client_email
        session['client_phone_number'] = client_phone_number
        session['client_company_name'] = client_company_name  # Add the company_name to the session data
        session['pickup_datetime'] = pickup_datetime_str  # Store as a string
        session['pickup_street'] = pickup_street
        session['pickup_city'] = pickup_city
        session['pickup_state'] = pickup_state
        session['pickup_zip'] = pickup_zip
        session['dropoff_street'] = dropoff_street
        session['dropoff_city'] = dropoff_city
        session['dropoff_state'] = dropoff_state
        session['dropoff_zip'] = dropoff_zip

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", client_email):
            return render_template('book.html', error="Invalid email address.", now=datetime.now(), **session)

        # Redirect to confirmation page
        return redirect(url_for('confirm'))

    # Retrieve session data for rendering the form
    client_first_name = session.get('client_first_name', '')
    client_last_name = session.get('client_last_name', '')
    client_email = session.get('client_email', '')
    client_phone_number = session.get('client_phone_number', '')
    client_company_name = session.get('client_company_name', '')  # Add this line
    pickup_datetime = session.get('pickup_datetime', '')
    pickup_time = pickup_datetime.strftime('%H:%M') if pickup_datetime else ''
    pickup_datetime_str = session.get('pickup_datetime', '')  # Retrieve as string
    pickup_street = session.get('pickup_street', '')
    pickup_city = session.get('pickup_city', '')
    pickup_state = session.get('pickup_state', '')
    pickup_zip = session.get('pickup_zip', '')
    dropoff_street = session.get('dropoff_street', '')
    dropoff_city = session.get('dropoff_city', '')
    dropoff_state = session.get('dropoff_state', '')
    dropoff_zip = session.get('dropoff_zip', '')

    # Render the booking form
    return render_template('book.html', client_first_name=client_first_name, client_last_name=client_last_name,
                           client_company_name=client_company_name,  # Add this line
                           client_email=client_email, client_phone_number=client_phone_number,
                           pickup_datetime=pickup_datetime_str, pickup_time=pickup_time,
                           pickup_street=pickup_street, pickup_city=pickup_city, pickup_state=pickup_state,
                           pickup_zip=pickup_zip, dropoff_street=dropoff_street, dropoff_city=dropoff_city,
                           dropoff_state=dropoff_state, dropoff_zip=dropoff_zip,
                           now=datetime.now())

# Confirmation route
@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    # Retrieve session data
    client_first_name = session.get('client_first_name', 'Unknown')
    client_last_name = session.get('client_last_name', '')
    client_email = session.get('client_email', '')
    client_phone_number = session.get('client_phone_number', '')
    pickup_datetime_str = session.get('pickup_datetime', '')
    pickup_datetime = datetime.strptime(pickup_datetime_str, '%Y-%m-%dT%H:%M') if pickup_datetime_str else None
    pickup_street = session.get('pickup_street', '')
    pickup_city = session.get('pickup_city', '')
    pickup_state = session.get('pickup_state', '')
    pickup_zip = session.get('pickup_zip', '')
    dropoff_street = session.get('dropoff_street', '')
    dropoff_city = session.get('dropoff_city', '')
    dropoff_state = session.get('dropoff_state', '')
    dropoff_zip = session.get('dropoff_zip', '')
    client_company_name = session.get('client_company_name', None)
    print(f"Company Name from Session: {client_company_name}")

    if request.method == 'POST':
        if 'cancel' in request.form:
            return redirect(url_for('home'))

        # Check if the client already exists in the database based on email and phone_number
        existing_client = Client.query.filter_by(
            email=client_email,
            phone_number=client_phone_number
        ).first()

        if existing_client:
            # If the client exists, update the company_name if a new one is provided
            if client_company_name is not None:
                existing_client.company_name = client_company_name
                db.session.commit()

        # Create a new client if it doesn't exist
        if not existing_client:
            existing_client = Client(
                first_name=client_first_name,
                last_name=client_last_name,
                email=client_email,
                phone_number=client_phone_number,
                company_name=client_company_name
            )
            db.session.add(existing_client)

        new_trip = Trip(
            client=existing_client,
            pickup_datetime=pickup_datetime,
            pickup_street=pickup_street,
            pickup_city=pickup_city,
            pickup_state=pickup_state,
            pickup_zip=pickup_zip,
            dropoff_street=dropoff_street,
            dropoff_city=dropoff_city,
            dropoff_state=dropoff_state,
            dropoff_zip=dropoff_zip,
            fare=0.0
        )
        # Set the invoice_date based on the date of the trip
        new_invoice = Invoice(
            trip=new_trip,
            invoice_date=pickup_datetime.date(),  # Set to the date of the trip
            total_amount=0.0
        )

        db.session.add(new_trip)
        db.session.add(new_invoice)
        db.session.commit()

        # Clear session data after processing
        session.pop('client_first_name', None)
        session.pop('client_last_name', None)
        session.pop('client_email', None)
        session.pop('client_phone_number', None)
        session.pop('pickup_datetime', None)
        session.pop('pickup_street', None)
        session.pop('pickup_city', None)
        session.pop('pickup_state', None)
        session.pop('pickup_zip', None)
        session.pop('dropoff_street', None)
        session.pop('dropoff_city', None)
        session.pop('dropoff_state', None)
        session.pop('dropoff_zip', None)

        # Redirect to thank you page
        return redirect(url_for('thank_you'))

    # Render the confirmation page
    return render_template('confirm.html', client_first_name=client_first_name, client_last_name=client_last_name,
                           client_email=client_email, client_phone_number=client_phone_number,
                           client_company_name=client_company_name,
                           pickup_datetime=pickup_datetime,
                           pickup_street=pickup_street, pickup_city=pickup_city, pickup_state=pickup_state,
                           pickup_zip=pickup_zip, dropoff_street=dropoff_street, dropoff_city=dropoff_city,
                           dropoff_state=dropoff_state, dropoff_zip=dropoff_zip)

# Thank you route
@app.route('/thank_you', methods=['GET', 'POST'])
def thank_you():
    # Render the thank you page
    return render_template('thank_you.html')

if __name__ == '__main__':
    # Create all database tables if they do not exist
    with app.app_context():
        db.create_all()
    # Run the Flask application in debug mode
    app.run(debug=True)
