from backend.database import db
from datetime import datetime

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    prediction = db.Column(db.Float)
    uncertainty = db.Column(db.Float)
    confidence_lower = db.Column(db.Float)
    confidence_upper = db.Column(db.Float)
    risk_score = db.Column(db.Float)
    severity = db.Column(db.String(20))
    data_source = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.String(20))
    message = db.Column(db.String(500))
    risk_score = db.Column(db.Float)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
