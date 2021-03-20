from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt


def send_email(sender, to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=sender
    )
    mail.send(msg)

class SecuritySerializer:

    def init(self, secret_key, salt, max_age):
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.salt = salt
        self.max_age = max_age


    def generate_confirmation_token(self, email):

        return self.serializer.dumps(
            email,
            salt=self.salt
        )

    def confirm(self, confirmation_token, max_age=-1):

        try:
            return self.serializer.loads(
                confirmation_token,
                salt=self.salt,
                max_age=self.max_age if max_age == -1 else max_age)

        except Exception:
            return False


mail = Mail()
bcrypt = Bcrypt()
security_serializer = SecuritySerializer()

def init_app(app):


    mail.init_app(app)
    bcrypt.init_app(app)
    security_serializer.init(
        secret_key=app.config['SECRET_KEY'],
        salt=app.config['SECURITY_SALT'],
        max_age=app.config['VERIFICATION_MAX_AGE'],
    )
