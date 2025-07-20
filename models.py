# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False) # 'secretariat' ou 'restaurant'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    service_demandeur = db.Column(db.String(100), nullable=False)
    responsable_email = db.Column(db.String(120), nullable=False)
    nombre_repas = db.Column(db.Integer, default=0)
    nombre_desserts = db.Column(db.Integer, default=0)
    nombre_limonades = db.Column(db.Integer, default=0)
    nombre_boissons_chaudes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    guests = db.relationship('Guest', backref='invitation', lazy=True, cascade="all, delete-orphan")

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    societe = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=True) 
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)