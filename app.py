import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;(enter as YYYY-MM-DD) Date Range is (2010-01-01 to 2017-08-23)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (enter as YYYY-MM-DD/YYYY-MM-DD)Date Range is (2010-01-01 to 2017-08-23)<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

   # Calculate the date one year from the last date in data set.
    latest_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
    latest_date = dt.datetime.strptime(latest_date_str, '%Y-%m-%d')
    query_one_year_date = latest_date - dt.timedelta(days = 365)
   
    # Perform a query to retrieve the data and precipitation scores
    prcp_data = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date >= query_one_year_date)
                  .order_by(Measurement.date)
                  .all())
    
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    # Convert List of Tuples Into a Dictionary
    prcp_data_dict = dict(prcp_data)


    #Return the JSON representation of your dictionary.
    return jsonify(prcp_data_dict)
    session.close()


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations
    query_stations = session.query(Station.station).all()

    # Convert List of Tuples Into Normal List
    stations_list = list(np.ravel(query_stations))

    # Return JSON List of Stations from the Dataset
    return jsonify(Stations = stations_list)

    session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Find active station
    active_stations = (session.query(Measurement.station,func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())

    stationID = active_stations[0][0]
    #calculate actual date
    latest_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
    latest_date = dt.datetime.strptime(latest_date_str, '%Y-%m-%d')
    query_one_year_date = latest_date - dt.timedelta(days = 365)

    tobs_data = session.query(Measurement.tobs).\
    filter(Measurement.date >= query_one_year_date).\
    filter(Measurement.station == stationID).\
    order_by(Measurement.date).all()

    # Convert List of Tuples Into Normal List
    tobs_data_list = list(np.ravel(tobs_data))

    # Return JSON List of Temperature Observations (tobs) for the Previous Year
    return jsonify(Temperature = tobs_data_list)
     
    session.close()

@app.route("/api/v1.0/<start>")
def startDate(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date

    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]

    temperature_start = session.query(*sel).\
                filter(Measurement.date >= start).\
                group_by(Measurement.date).all()


    dates = []                       
    for result in temperature_start:
        date_dict = {}
        date_dict["Min Temp"] = result[0]
        date_dict["Max Temp"] = result[1]
        date_dict["Avg Temp"] = '{:.2f}'.format(result[2])
        dates.append(date_dict)

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
    return jsonify(dates)
   
    session.close()

@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]

    temperature_start_end = session.query(*sel).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.date).all()

    dates = []                       
    for result in temperature_start_end:
        date_dict = {}
        date_dict["Min Temp"] = result[0]
        date_dict["Max Temp"] = result[1]
        date_dict["Avg Temp"] = '{:.2f}'.format(result[2])
        dates.append(date_dict)


    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date and end date
    return jsonify(dates)

    session.close()

if __name__ == '__main__':
    app.run(debug=True)
