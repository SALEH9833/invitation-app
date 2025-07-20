# app.py

# --- IMPORTS NÉCESSAIRES ---
from dotenv import load_dotenv
import os
import datetime
from sqlalchemy import func

load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_mail import Mail, Message
from weasyprint import HTML
import io
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import Config
from models import db, User, Invitation, Guest
from forms import LoginForm, InvitationForm

# --- CONFIGURATION ET INITIALISATIONS ---
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "info"
mail = Mail(app)

# --- GESTION DES UTILISATEURS ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command("create-users")
def create_users():
    if User.query.filter_by(email='secretaire@cimentsdumaroc.ma').first() is None:
        user_secretariat = User(email='secretaire@cimentsdumaroc.ma', role='secretariat')
        user_secretariat.set_password('test123')
        db.session.add(user_secretariat)
        print("Utilisateur 'secretaire@cimentsdumaroc.ma' créé.")
    if User.query.filter_by(email='restaurant@cimentsdumaroc.ma').first() is None:
        user_restaurant = User(email='restaurant@cimentsdumaroc.ma', role='restaurant')
        user_restaurant.set_password('test123')
        db.session.add(user_restaurant)
        print("Utilisateur 'restaurant@cimentsdumaroc.ma' créé.")
    db.session.commit()
    print("Opération terminée.")

# --- ROUTES D'AUTHENTIFICATION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou mot de passe invalide.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROUTE PRINCIPALE (HUB) ---
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'secretariat':
        return render_template('secretariat/dashboard.html')
    
    elif current_user.role == 'restaurant':
        invitations_en_attente = Invitation.query.filter_by(status='pending').order_by(Invitation.created_at.asc()).all()
        invitations_traitees = Invitation.query.filter(Invitation.status.in_(['accepted', 'rejected'])).order_by(Invitation.created_at.desc()).all()
        return render_template('restaurant/dashboard.html', invitations_en_attente=invitations_en_attente, invitations_traitees=invitations_traitees)
    
    else:
        flash("Votre rôle n'est pas défini. Déconnexion.", "danger")
        logout_user()
        return redirect(url_for('login'))

# --- ROUTES SECRÉTARIAT ---
@app.route('/secretariat/invitation/nouvelle', methods=['GET', 'POST'])
@login_required
def nouvelle_invitation():
    if current_user.role != 'secretariat':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    form = InvitationForm()
    if form.validate_on_submit():
        nouvelle_invit = Invitation(service_demandeur=form.service_demandeur.data, responsable_email=form.responsable_email.data, nombre_repas=form.nombre_repas.data, nombre_desserts=form.nombre_desserts.data, nombre_limonades=form.nombre_limonades.data, nombre_boissons_chaudes=form.nombre_boissons_chaudes.data, user_id=current_user.id, status='pending')
        
        # === RÉCUPÉRATION DES EMAILS DES INVITÉS ===
        noms_invites = request.form.getlist('nom_invite[]')
        emails_invites = request.form.getlist('email_invite[]')
        societes_invites = request.form.getlist('societe_invite[]')

        guest_emails_to_notify = []

        for nom, email, societe in zip(noms_invites, emails_invites, societes_invites):
            if nom:
                guest = Guest(nom=nom, email=email, societe=societe)
                nouvelle_invit.guests.append(guest)
                if email:
                    guest_emails_to_notify.append(email)

        db.session.add(nouvelle_invit)
        db.session.commit()
        
        html_pour_pdf = render_template('pdf/invitation_template.html', invitation=nouvelle_invit)
        pdf_file_bytes = HTML(string=html_pour_pdf, base_url=request.url_root).write_pdf()
        
        try:
            # === MISE À JOUR DES DESTINATAIRES ===
            destinataires = [nouvelle_invit.responsable_email, 'restaurant@cimentsdumaroc.ma']
            destinataires.extend(guest_emails_to_notify)
            destinataires = list(set(destinataires))

            msg = Message(
                subject=f"Invitation au Restaurant - Ciments du Maroc",
                sender=('Ciments du Maroc - GestInv', app.config['MAIL_USERNAME']),
                recipients=destinataires
            )
            msg.body = f"Bonjour,\n\nVous êtes cordialement invité(e) à un repas au restaurant de Ciments du Maroc, organisé par le service {nouvelle_invit.service_demandeur}.\n\nVous trouverez les détails de l'invitation en pièce jointe."
            
            msg.attach(f'invitation-{nouvelle_invit.id}.pdf', 'application/pdf', pdf_file_bytes)
            
            mail.send(msg)
            flash('Invitation envoyée et notifiée par email avec succès !', 'success')
        except Exception as e:
            flash(f'L\'invitation a été créée, mais l\'envoi de l\'email a échoué. Erreur: {e}', 'danger')
        
        return redirect(url_for('dashboard', download_pdf_id=nouvelle_invit.id))

    date_du_jour_iso = datetime.date.today().isoformat()
    return render_template('secretariat/new_invitation.html', form=form, date_du_jour_iso=date_du_jour_iso)

# ... (toutes les autres routes restent les mêmes et sont correctes) ...
@app.route('/secretariat/historique')
@login_required
def historique_secretariat():
    if current_user.role != 'secretariat':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    invitations = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.created_at.desc()).all()
    return render_template('secretariat/history.html', invitations=invitations)

@app.route('/secretariat/statistiques')
@login_required
def statistiques_secretariat():
    if current_user.role != 'secretariat':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query_invitations = Invitation.query
    query_guests = Guest.query.join(Invitation)

    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query_invitations = query_invitations.filter(Invitation.created_at >= start_date)
        query_guests = query_guests.filter(Invitation.created_at >= start_date)
    
    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        end_date_inclusive = end_date + datetime.timedelta(days=1)
        query_invitations = query_invitations.filter(Invitation.created_at < end_date_inclusive)
        query_guests = query_guests.filter(Invitation.created_at < end_date_inclusive)

    stats_par_statut = query_invitations.with_entities(Invitation.status, func.count(Invitation.id)).group_by(Invitation.status).all()
    stats = {status: count for status, count in stats_par_statut}
    stats_par_societe = query_guests.filter(Guest.societe.isnot(None), Guest.societe != '').with_entities(Guest.societe, func.count(Guest.id)).group_by(Guest.societe).order_by(func.count(Guest.id).desc()).all()
    total_invitations = query_invitations.count()

    return render_template('secretariat/stats.html', stats=stats, stats_par_societe=stats_par_societe, total_invitations=total_invitations)

@app.route('/restaurant/invitation/<int:invitation_id>/<string:action>', methods=['POST'])
@login_required
def traiter_invitation(invitation_id, action):
    if current_user.role != 'restaurant':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    invitation = Invitation.query.get_or_404(invitation_id)
    if invitation.status != 'pending':
        flash("Cette invitation a déjà été traitée.", "warning")
        return redirect(url_for('dashboard'))
    if action == 'accepter':
        invitation.status = 'accepted'
        flash(f"L'invitation #{invitation.id} a été acceptée.", "success")
    elif action == 'refuser':
        invitation.status = 'rejected'
        flash(f"L'invitation #{invitation.id} a été refusée.", "danger")
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/download/pdf/<int:invitation_id>')
@login_required
def download_pdf(invitation_id):
    invitation = Invitation.query.get_or_404(invitation_id)
    if current_user.role == 'secretariat' and invitation.user_id != current_user.id:
        flash("Accès non autorisé à ce PDF.", "danger")
        return redirect(url_for('dashboard'))
    html_pour_pdf = render_template('pdf/invitation_template.html', invitation=invitation)
    pdf_file = io.BytesIO(HTML(string=html_pour_pdf, base_url=request.url_root).write_pdf())
    return send_file(pdf_file, mimetype='application/pdf', as_attachment=True, download_name=f'invitation-{invitation.id}.pdf')

@app.route('/secretariat/historique/download')
@login_required
def download_history_pdf():
    if current_user.role != 'secretariat':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    query = Invitation.query.filter_by(user_id=current_user.id)
    start_date_display, end_date_display = "Début", "Aujourd'hui"
    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(Invitation.created_at >= start_date)
        start_date_display = start_date.strftime('%d-%m-%Y')
    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        end_date_inclusive = end_date + datetime.timedelta(days=1)
        query = query.filter(Invitation.created_at < end_date_inclusive)
        end_date_display = end_date.strftime('%d-%m-%Y')
    invitations = query.order_by(Invitation.created_at.desc()).all()
    html = render_template('pdf/history_pdf.html', invitations=invitations, start_date=start_date_display, end_date=end_date_display)
    pdf = HTML(string=html, base_url=request.url_root).write_pdf()
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name='rapport_historique.pdf')

@app.route('/secretariat/statistiques/download')
@login_required
def download_stats_pdf():
    if current_user.role != 'secretariat':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('dashboard'))
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    query_invitations = Invitation.query
    query_guests = Guest.query.join(Invitation)
    start_date_display, end_date_display = "Début", "Aujourd'hui"
    if start_date_str:
        start_date_obj = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query_invitations = query_invitations.filter(Invitation.created_at >= start_date_obj)
        query_guests = query_guests.filter(Invitation.created_at >= start_date_obj)
        start_date_display = start_date_obj.strftime('%d-%m-%Y')
    if end_date_str:
        end_date_obj = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        end_date_inclusive = end_date_obj + datetime.timedelta(days=1)
        query_invitations = query_invitations.filter(Invitation.created_at < end_date_inclusive)
        query_guests = query_guests.filter(Invitation.created_at < end_date_inclusive)
        end_date_display = end_date_obj.strftime('%d-%m-%Y')
    stats_par_statut = query_invitations.with_entities(Invitation.status, func.count(Invitation.id)).group_by(Invitation.status).all()
    stats = {status: count for status, count in stats_par_statut}
    stats_par_societe = query_guests.filter(Guest.societe.isnot(None), Guest.societe != '').with_entities(Guest.societe, func.count(Guest.id)).group_by(Guest.societe).order_by(func.count(Guest.id).desc()).all()
    total_invitations = query_invitations.count()
    html = render_template('pdf/stats_pdf.html', stats=stats, stats_par_societe=stats_par_societe, total_invitations=total_invitations, start_date=start_date_display, end_date=end_date_display)
    pdf = HTML(string=html, base_url=request.url_root).write_pdf()
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name='rapport_statistiques.pdf')