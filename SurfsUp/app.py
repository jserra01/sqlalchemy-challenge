# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all available api routes."""
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/&ltstart&gt - required date format for &ltstart&gt: YYYY-MM-DD<br/>'
        f'/api/v1.0/&ltstart&gt/&ltend&gt - required date format for &ltstart&gt and &ltend&gt: YYYY-MM-DD<br/>'
    )



@app.route('/api/v1.0/precipitation')
def precipitation():
    
    #Query data
    start_date = dt.datetime(2017, 8, 23)
    end_date = start_date - dt.timedelta(days=365)
       
    query_results = session.query(Measurement.date, func.max(Measurement.prcp)).\
            filter(Measurement.date <= start_date.strftime('%Y-%m-%d')).\
            filter(Measurement.date >= end_date.strftime('%Y-%m-%d')).\
            group_by(Measurement.date).order_by(Measurement.date.asc()).all()
    
    #Convert into normal list
    all_data = []
    for date, precipitation in query_results:
        prcp_dict = {}
        prcp_dict[date] = precipitation
        all_data.append(prcp_dict)
    
    session.close()
    
    return jsonify(all_data)

@app.route('/api/v1.0/stations')
def stations():
    
    #Query data
    query_results1 = session.query(Station.station, Station.name).distinct().all()
    
    #Convert to list
    station_data = []
    for station, name in query_results1:
        stn_dict = {}
        stn_dict[station] = name
        station_data.append(stn_dict)
        
    session.close()
    
    return jsonify(station_data)

@app.route('/api/v1.0/tobs')
def tobs():
    
    #Query data
    start_date = dt.datetime(2017, 8, 23)

    end_date = start_date - dt.timedelta(days=365)
        
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).first()

    active_station_id = active_station[0]
    
    query_results2 = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date <= start_date.strftime('%Y-%m-%d')).\
            filter(Measurement.date >= end_date.strftime('%Y-%m-%d')).\
            filter(Measurement.station == active_station_id).\
            order_by(Measurement.date.asc()).all()

    #Convert to list
    tobs_data = []
    for date, temp in query_results2:
        temp_dict = {}
        temp_dict[date] = temp
        tobs_data.append(temp_dict)
        
    session.close()
    
    return jsonify(tobs_data)
        
@app.route('/api/v1.0/<start>')
def temp_greater_than_date(start):
    
    #Check User Start Date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()
    
    date_check = False
    
    if start >= first_date[0]:
        if start <= last_date[0]:
            date_check = True
    
    if date_check == True:
        
        #Query Results
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        query_results3 = session.query(*sel).filter(Measurement.date >= start).all()
        
        #Convert to list
        data1 = []
        for min_, avg_, max_ in query_results3:
            data1_dict = {}
            data1_dict['minimum temperature'] = min_
            data1_dict['average temperature'] = avg_
            data1_dict['maximum temperature'] = max_
            data1.append(data1_dict)
    
        session.close()
        
        return jsonify(data1)
    
    return jsonify({'error': f'Date {start} not in the appropriate format (YYYY-MM-DD) or not within available data.'}), 404
    
@app.route('/api/v1.0/<start>/<end>')
def temp_between_date(start, end):
    
    #Check User Start Date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()
    
    date_check = False
    
    if first_date[0] <= start <= last_date[0]:
        if start <= end <= last_date[0]:
            date_check = True
    
    if date_check == True:
        
        #Query Results
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        query_results4 = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
        #Convert to list
        data2 = []
        for min_, avg_, max_ in query_results4:
            data2_dict = {}
            data2_dict['minimum temperature'] = min_
            data2_dict['average temperature'] = avg_
            data2_dict['maximum temperature'] = max_
            data2.append(data2_dict)
    
        session.close()
        
        return jsonify(data2)
    
    return jsonify({'error': f'Dates must be in YYYY-MM-DD with end date after start date and within available data.'}), 404
    
    
if __name__ == "__main__":
    app.run(debug=True)

