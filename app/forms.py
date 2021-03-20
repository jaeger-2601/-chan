from datetime import date
from .models import Users

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields import StringField, PasswordField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import Email, InputRequired, Length, EqualTo, ValidationError

class CharactersAllowed:

    def __init__(self, chars_allowed, message=None):
        self.chars_allowed = chars_allowed
        self.message = message if not message == None else 'Character {} not allowed'
    
    def __call__(self, form, field):
        
        for letter in field.data:
            if letter not in self.chars_allowed:
                raise ValidationError(self.message.format(character=letter))
        
class UniqueUserAttr:

    def __init__(self, attr_name, message=None):
        self.attr_name = attr_name
        self.message = message if not message == None else f'{attr_name} should be unique'

    def __call__(self, form, field):

        if not Users.is_unique(self.attr_name, field.data):
            raise ValidationError(self.message)

class SignupForm(FlaskForm):


    user_name = StringField(
        validators=[
            InputRequired(message='User name required!'),
            Length(min=1, max=60, message='User name should be between 1 and 60 chars!'),
            CharactersAllowed(
                chars_allowed='abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-', 
                message='Character {character} not allowed in username!'
            ),
            UniqueUserAttr('uname', message='User name taken'),
        ]
    )
    email = EmailField(
        validators=[
            Email(message='Invalid email!'),
            InputRequired(message='Email required!'),
            Length(min=5, max=100, message='Email too big!'),
            UniqueUserAttr('email', message='Email already registered'),
        ]
    )

    password = PasswordField(
        validators=[
            InputRequired(message='Password required!'),
            Length(min=6, max=100, message='Password should be 6 and 100 chars!'),
            EqualTo('password_repeat', message='Passwords should match!')
        ]
    )

    password_repeat = PasswordField(
        validators=[
            InputRequired(message='Password should be rentered!'),
        ]
    )

    birth_date = DateField(
        validators=[
            InputRequired(message='Date of Birth required!'),
        ]
    )

    @staticmethod
    def validate_birth_date(form, field):
        if (date.today() - field.data).days < (13 * 365):
            raise ValidationError('Must be atleast 13 years old!')



class LoginForm(FlaskForm):

    email = EmailField(
        validators=[
            Email(message='Not a email!'),
            InputRequired(message='Email required!'),
            Length(min=5, max=100, message='Email too big!'),
        ]
    )

    password = PasswordField(
        validators=[
            InputRequired(message='Password required!'),
            Length(min=6, max=100, message='Password should be 6 and 100 chars!'),
        ]
    )

'''
     if form.profile_pic.data != None:
            ext =  form.profile_pic.data.filename.rsplit('.', 1)[1].lower()
            filename = join(
                'app',
                current_app.config['IMG_UPLOADS_DIR'], 
                'profile', 
                f'{str(uuid4())}.{ext}'
            )

            #save the image 
            form.profile_pic.data.save(filename)

    profile_pic = FileField (
        validators=[
            FileAllowed(['png', 'jpg', 'jpeg', 'gif'], message='Images only!'),        
        ]
    )
'''