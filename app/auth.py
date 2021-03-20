

from flask import Blueprint, redirect, render_template, request, flash, current_app, url_for, session
from .models import Users, Boards, Threads, Posts
from .forms import SignupForm, LoginForm
from .utils import mail, bcrypt, security_serializer ,send_email
from uuid import uuid4
from datetime import date
from os.path import join, abspath

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignupForm()
  
    if form.validate_on_submit():

        Users.add(
            UNAME = form.user_name.data,
            EMAIL = form.email.data,
            PWDHASH = bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            DOB = form.birth_date.data,

        )
        
        token = security_serializer.generate_confirmation_token(form.email.data)
        confirm_url = url_for('auth.verify_email', confirmation_token = token, _external=True)

        send_email(
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            to=form.email.data,
            subject='Mu-chan confirmation email',
            template=f'Please click this link to confirm your account.\n {confirm_url}'
        )

        #template
        return 'Confirmation email sent again'
    #template
    return render_template('signup.html', form=form)

@auth_bp.route('/resend/<resend_token>')
def resend(resend_token):

    email = security_serializer.confirm(resend_token, max_age=None)

    if email == False:
        flash('Cannot resend email, resend token is unverified!')
        #template
        return 'Cannot resend email, resend token is unverified!'

    if Users.is_registered(EMAIL = email):
        if not Users.is_confirmed(EMAIL = email):
            #resend the confirmation token
            token = security_serializer.generate_confirmation_token(email)
            confirm_url = url_for('auth.verify_email', confirmation_token = token, _external=True)

            send_email(
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                to=email,
                subject='Mu-chan confirmation email',
                template=f'Please click this link to confirm your account.\n {confirm_url}'
            )
            session['email'] = email
            return redirect(url_for('auth.unconfirmed'))
        else:
            #template
            return 'Already confirmed!'
    #template
    return 'Email not registered! Please register again!'


@auth_bp.route('/unconfirmed')
def unconfirmed():
    token = security_serializer.generate_confirmation_token(session.pop('email'))
    #template
    return f'''
    Please verify your email to register your account. <a href="{url_for('auth.resend', resend_token = token)}"> resend email </a>
    '''

@auth_bp.route('/confirm/<confirmation_token>')
def verify_email(confirmation_token):

    #! CHECK IF ACCOUNT IS ALREADY REGISTERED
    
    email = security_serializer .confirm(confirmation_token)

    if email == False:
        #template
        return 'The confirmation link is invalid or has expired.'
    

    #! MAKE THIS MORE SECURE! SQL INJECTION POSSIBLE
    Users.update(
        DOJ = date.today(),
        condition = f"EMAIL = '{email}'")
    #template
    return 'Email verified'

@auth_bp.route('/signin', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        pass
    #template
    return render_template('login.html', form=form)

@auth_bp.route('/signout')
def signout():
    pass

'''/static/* - for static files like images, js, css etc.

/signup/ -  for sign up

/login/ -  for login

/board/<>?sort_by=<> - for seeing threads related to a specific board

/board/<>/thread/<>?sort_by=<> - for seeing posts related to a thread

/board/<>/thread/<>/modify - for modifying or deleting a thread

/board/<>/thread/<>/post/<> - for seeing a specific post in a thread

/board/<>/thread/<>/post/<>/modify - for modifying or deleting a post

/user/<> - for seeing user related info

/user/<>/modify - modifying user info or deleting user info'''