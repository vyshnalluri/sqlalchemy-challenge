import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


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
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def Precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    sel = [Measurement.date, Measurement.prcp]
    query_result = session.query(*sel).all()
    session.close()

    # Convert list of tuples into normal list
    precipitation = []
    for date, prcp in query_result:
        prcp_dic = {date:prcp}
        #prcp_dic["Date"] = date
        #prcp_dic["Precipitation"] = prcp
        precipitation.append(prcp_dic)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def Stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    sel = [Station.station,Station.name]
    query_result = session.query(*sel).all()
    session.close()

    stations = []
    for station,name in query_result:
        station_dic = {}
        station_dic["Station"] = station
        station_dic["Name"] = name
        stations.append(station_dic)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def Tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #active stations
    sel = [Measurement.station,func.count(Measurement.id)]
    active_stations = session.query(*sel).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).all()
    active_stations
    
    #year ago data
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], "%Y-%m-%d")
    year_ago = dt.date(recent_date.year -1, recent_date.month, recent_date.day)

    # Query all passengers
    query_result = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == active_stations[0][0]).all()
    session.close()
    
    tobs_list = []
    for date,tobs in query_result:
        tob_dic = {}
        tob_dic["Date"] = date
        tob_dic["Temperature"] = tobs
        tobs_list.append(tob_dic)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temp_start = []
    for tmin,tavg,tmax in query_result:
        temp_dic = {}
        temp_dic["Min Temp"] = tmin
        temp_dic["Average Temp"] = tavg
        temp_dic["Max Temp"] = tmax
        temp_start.append(temp_dic)

    return jsonify(temp_start)

@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start,end):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_start_end = []
    for tmin,tavg,tmax in query_result:
        temp_dic = {}
        temp_dic["Min Temp"] = tmin
        temp_dic["Average Temp"] = tavg
        temp_dic["Max Temp"] = tmax
        temp_start_end.append(temp_dic)

    return jsonify(temp_start_end)

if __name__ == '__main__':
    app.run(debug=True)
