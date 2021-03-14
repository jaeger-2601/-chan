import psycopg2
import time

class Database:

    def __init__(self, app):

        self.app = app

        try:
            print('Connecting to PostgreSQL database')

            self.connection = psycopg2.connect(
                database=app.config['DB_NAME'], 
                user=app.config['DB_USER'], 
                password=app.config['DB_PASSWORD'], 
                host=app.config['DB_HOST'], 
                port=app.config['DB_PORT']
            )

            self.cursor = self.connection.cursor()


        except Exception as error:
            raise ConnectionError('Could not connect to PostgreSQL database') from error
            
        else:
            print('Connection established with database!')

        self.__del__ = self.app.teardown_appcontext(self.__del__)

    def query(self, query):
        try:
            result = self.cursor.execute(query)
        except Exception as error:
            print('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def __del__(self):
        print('Closing connection to database. Goodbye')
        self.connection.close()
        self.cursor.close()

class Model:

    schema = ''

    def __init_subclass__(cls, **kwargs):
        pass
    
    @classmethod
    def _set_db(cls, db):
        cls.db = db


    @classmethod
    def create(cls) -> None:
        print(f'Creating table for {cls.__name__}')
        cls.db.cursor.execute(cls.schema)


class Users(Model):
    
    schema = '''

        DROP TYPE IF EXISTS USER_TYPE CASCADE;
        CREATE TYPE USER_TYPE AS ENUM (
            'MODERATOR', 'USER'
        );

        CREATE TABLE IF NOT EXISTS USERS (
            UID SERIAL PRIMARY KEY,
            UNAME VARCHAR(60) UNIQUE NOT NULL,
            EMAIL VARCHAR(60) UNIQUE NOT NULL,
            PWDHASH CHAR(60) NOT NULL,
            DOJ DATE,
            DOB DATE NOT NULL,
            PIC VARCHAR(200),
            UTYPE USER_TYPE DEFAULT 'USER'
        );
    '''

class Boards(Model):     
    
    schema = '''
        CREATE TABLE IF NOT EXISTS BOARDS (
            BID SERIAL PRIMARY KEY,
            BNAME VARCHAR(60) UNIQUE NOT NULL,
            URL VARCHAR(200) UNIQUE NOT NULL,
            TITLE VARCHAR(60) NOT NULL,
            DESCRIPTION VARCHAR(200) NOT NULL,
            PIC VARCHAR(200)
        );
    '''  
    
class Threads(Model):

    schema = '''
        CREATE TABLE IF NOT EXISTS THREADS (
            TID SERIAL PRIMARY KEY,
            URL VARCHAR(200) UNIQUE NOT NULL,
            TITLE VARCHAR(200) NOT NULL,
            DESCRIPTION VARCHAR(40000),
            PIC VARCHAR(200),
            UPVOTES INT NOT NULL DEFAULT 0,
            BID INT REFERENCES BOARDS(BID),
            UID INT REFERENCES USERS(UID) ON DELETE SET NULL
        );
    '''   
   
class Posts(Model):

    schema = '''
        CREATE TABLE IF NOT EXISTS POSTS (
            PID SERIAL PRIMARY KEY,
            URL VARCHAR(200) UNIQUE NOT NULL,
            TEXT VARCHAR(40000),
            PIC VARCHAR(200),
            UPVOTES INT NOT NULL DEFAULT 0,
            TID INT REFERENCES THREADS(TID) ON DELETE CASCADE,
            UID INT REFERENCES USERS(UID) ON DELETE SET NULL
        );
    '''


def init_app(app):

    Model._set_db(Database(app))

    for model in Model.__subclasses__():
        model.create()

    Model.db.connection.commit()