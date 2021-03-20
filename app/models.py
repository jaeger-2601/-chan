import psycopg2.pool

class Database:

    def __init__(self, app):

        try:
            print('Connecting to PostgreSQL database')

            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                database=app.config['DB_NAME'], 
                user=app.config['DB_USER'], 
                password=app.config['DB_PASSWORD'], 
                host=app.config['DB_HOST'], 
                port=app.config['DB_PORT']
            )

          
        except Exception as error:
            raise ConnectionError('Could not connect to PostgreSQL database') from error
            
        else:
            print('Connection established with database.')

    def query(self, query, vars_=(), fetch=False, commit=True):

        try:
            connection = self.connection_pool.getconn()

            with connection.cursor() as cursor:           
                cursor.execute(query, vars_)
                
                if commit:
                    connection.commit()

                result = [] if not fetch else cursor.fetchall()

            self.connection_pool.putconn(connection)
            return result

        except Exception as error:
            print('Error execting query "{}", error: {}'.format(query, error))
            return None


    def close_db(self, *args, **kwargs):
        print('Closing connection to database. Goodbye')
        self.connection_pool.closeall()
    
    def __del__(self):
        self.close_db()

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
        cls.db.query(cls.schema)

    @classmethod
    def add(cls, **attributes):
        
        query_string = f''' 
        INSERT INTO {cls.__name__.upper()}({','.join([attr.upper() for attr in attributes.keys()])})
        VALUES({','.join(['%s' for _ in attributes.keys()])});'''
        
        cls.db.query(
            query_string, 
            vars_= (*attributes.values(),), 
            commit=True
        )
        
    @classmethod
    def update(cls, condition, **attributes):

        query_string = f'''
        UPDATE {cls.__name__.upper()}
        SET {','.join([attr.upper() + ' = %s' for attr in attributes.keys()])}
        WHERE {condition};'''

        cls.db.query(
            query_string, 
            vars_= (*attributes.values(),), 
            commit=True
        )
        

class Users(Model):
    
    schema = '''

        /* DROP TYPE IF EXISTS USER_TYPE CASCADE;
        CREATE TYPE USER_TYPE AS ENUM (
            'MODERATOR', 'USER'
        ); */

        CREATE TABLE IF NOT EXISTS USERS (
            UID SERIAL PRIMARY KEY,
            UNAME VARCHAR(60) UNIQUE NOT NULL,
            EMAIL VARCHAR(100) UNIQUE NOT NULL,
            PWDHASH CHAR(60) NOT NULL,
            DOJ DATE,
            DOB DATE NOT NULL,
            PIC VARCHAR(200),
            UTYPE USER_TYPE DEFAULT 'USER'
        );
    '''

    @classmethod
    def is_unique(cls, attribute, value) -> bool:

        return len(
            cls.db.query(
                f'''
                SELECT * FROM {cls.__name__.upper()}
                WHERE {attribute.upper()} = %s;
                ''', 
                vars_=(value,),
                fetch=True
            )
        ) == 0

    @classmethod
    def is_registered(cls, **attributes) -> bool:

        return len(
            cls.db.query(
                f'''
                SELECT UID FROM {cls.__name__.upper()}
                WHERE {' AND '.join([attr.upper() + ' = %s' for attr in attributes.keys()])};
                ''',
                vars_=(*attributes.values(), ),
                fetch=True,
            )

        ) == 1

    @classmethod
    def is_confirmed(cls, **attributes) -> bool:

        return len(
            cls.db.query(
                f'''
                SELECT UID FROM {cls.__name__.upper()}
                WHERE {' AND '.join([attr.upper() + ' = %s' for attr in attributes.keys()])}
                AND DOJ IS NOT NULL;
                ''',
            vars_=(*attributes.values(), ),
            fetch=True,
            )
        ) == 1
        

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

    @app.cli.command('create_tables')
    def create_tables():
        for model in Model.__subclasses__():
            model.create()

    

