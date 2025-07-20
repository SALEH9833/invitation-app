# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange

class LoginForm(FlaskForm):
    # === MODIFICATION DES LABELS ICI ===
    email = StringField('Nom d\'utilisateur', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

# ... la classe InvitationForm ne change pas ...
class InvitationForm(FlaskForm):
    service_demandeur = StringField('Service Demandeur', validators=[DataRequired()])
    responsable_email = StringField("Email du Responsable (pour notification)", validators=[DataRequired(), Email()])
    nombre_repas = IntegerField('Nombre de repas servis', default=0, validators=[DataRequired(), NumberRange(min=0)])
    nombre_desserts = IntegerField('Desserts', default=0, validators=[DataRequired(), NumberRange(min=0)])
    nombre_limonades = IntegerField('Limonades', default=0, validators=[DataRequired(), NumberRange(min=0)])
    nombre_boissons_chaudes = IntegerField('Boissons chaudes', default=0, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Envoyer l'invitation")