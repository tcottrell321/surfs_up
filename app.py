import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# enable access and query of database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into our classes
Base = automap_base()

# Reflect the tables into SQLAlchemy
Base.prepare(engine, reflect=True)

# Create a variable for each of the classes (and what that class object returns)
measurement = Base.classes.measurement
station = Base.classes.station

# Create a session link from Python to our database 
session = Session(engine)

# Create a Flask application called app where '_name_' is a name variable
app = Flask(__name__)

# Define the root route for the welcome screen
@app.route("/")

# Define a function to return the other routes and add "V1.0" version of app
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# To run code in anaconda bring up anaconda shell and navigate to 
# directory   cd desktop/class_ds/surfs_up
# then type set FLASK_APP=app.py
# then flask run

# Build Precipitation route and function to retrieve precipitation for past year
# http://127.0.0.1:5000/api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Build the Stations route and function and return stations ID
# http://127.0.0.1:5000/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations) 

# Build the temperature route to return the monthly temperature from most active station
# then unravel the results into a one-demensional array and convert that array into a list to jsonify 
# http://127.0.0.1:5000/api/v1.0/tobs 
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()

    temps = list(np.ravel(results))
    return jsonify(temps)

# Build the statistics route to return statistics on temperature data providing start and end date
# http://127.0.0.1:5000/api/v1.0/temp/2017-06-01/2017-06-30
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
     app.run(debug=True)
