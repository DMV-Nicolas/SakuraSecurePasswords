import os

DBDIR=f"sqlite:///{os.path.abspath(os.getcwd())}/database.db"
DB_URI="mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
    username="ild1d1MfPL",
    password="t6CmS0xJ4q",
    hostname="remotemysql.com",
    databasename="ild1d1MfPL"
)
class Config(object):
    DEBUG=False
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_POOL_RECYCLE=250
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'sakura.securepass@gmail.com'
    MAIL_PASSWORD = 'i**097SakuraCnCode675412IndeskptNick**3412'

class ProductionConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI=DB_URI
    SECRET_KEY=os.environ["SECRET_KEY"]

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI=DBDIR
    SECRET_KEY=os.environ["SECRET_KEY"]
