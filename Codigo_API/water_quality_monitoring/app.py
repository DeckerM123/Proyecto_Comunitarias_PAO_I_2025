from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from resources.sensor_resource import blp as Sensor
from resources.measurement_resource import blp as Measurement
from resources.report_resource import blp as Report
from db import db
import models

def create_app():
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_quality_monitoring.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        inspector = db.inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()
    app.register_blueprint(Sensor)
    app.register_blueprint(Measurement)
    app.register_blueprint(Report)
    return app
