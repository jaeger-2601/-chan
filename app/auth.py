

from flask import Blueprint, redirect, render_template, request, flash, current_app, url_for, session
from flask_session import Session
from .models import Users, Boards, Threads, Posts
from .forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .utils import mail, bcrypt, security_serializer ,send_email
from uuid import uuid4
from datetime import date
from os.path import join, abspath

auth_bp = Blueprint('auth', __name__)
server_session = Session()

def init_app(app):
    server_session.init_app(app)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignupForm()
    
    #if user is logged in
    if 'user' in session:
        #TODO : change this
        return redirect(url_for('auth.signup'))

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

        session['email'] = form.email.data
        return redirect(url_for('auth.unconfirmed'))
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
    if 'email' in session:
        token = security_serializer.generate_confirmation_token(session.pop('email'))
        #template
        return f'''
        Please verify your email to register your account. <a href="{url_for('auth.resend', resend_token = token)}"> resend email </a>
        '''
    else:
        return redirect('/')

@auth_bp.route('/confirm/<confirmation_token>')
def verify_email(confirmation_token):

    #! CHECK IF ACCOUNT IS ALREADY REGISTERED
    
    email = security_serializer .confirm(confirmation_token)

    if email == False:
        #template
        return 'The confirmation link is invalid or has expired.'
    

    #! MAKE THIS MORE SECURE! SQL INJECTION POSSIBLE
    Users.update(
        DOJ=date.today(),
        condition=f"EMAIL = %s",
        condition_vars=(email,)
    )
    #template
    return 'Email verified'

@auth_bp.route('/signin', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        if Users.is_confirmed(EMAIL = form.email.data):
            
            user = Users.get_user_info(EMAIL = form.email.data)[0]
            
            if bcrypt.check_password_hash(user.pwdhash, form.password.data):
                session['user'] = user._asdict()
                return f''' {session['user']} '''
            else:
                #template
                return 'Wrong email/password!'

        elif Users.is_registered(EMAIL = form.email.data):
            session['email'] = form.email.data
            return redirect(url_for('auth.unconfirmed'))
        else:
            #template
            return 'User not found!'
            
    #template
    return render_template('login.html', form=form)

@auth_bp.route('/signout')
def signout():
    
    if 'user' in session:
        flash('logged out successfully')
    session.pop('user', None)
    return redirect('/')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    
    form = ForgotPasswordForm()

    if form.validate_on_submit():

        token = security_serializer.generate_confirmation_token(form.email.data)
        confirm_url = url_for('auth.reset_password', confirmation_token = token, _external=True)

        send_email(
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            to=form.email.data,
            subject='Mu-chan reset password',
            template=f'Please click this link to reset your password.\n {confirm_url}'
        )

        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form, post_url=confirm_url)

        
@auth_bp.route('/reset_password/<confirmation_token>', methods=['GET', 'POST'])
def reset_password(confirmation_token):
    
    form = ResetPasswordForm()
    email = security_serializer.confirm(confirmation_token, max_age=60 * 60)

    if email == False:
        flash('Cannot reset password. link is invalid or has expired')
        #template
        return 'Cannot reset password. link is invalid or has expired'

    if form.validate_on_submit():

        #! MAKE THIS MORE SECURE! SQL INJECTION POSSIBLE
        Users.update(
            PWDHASH=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            condition=f"EMAIL = %s",
            condition_vars=(email,)
        )

        #template
        return 'Password reset!'
    return render_template('reset_password.html', form=form, post_url=url_for('auth.reset_password', confirmation_token=confirmation_token))