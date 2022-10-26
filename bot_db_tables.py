import sqlalchemy as sq
import psycopg2
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DSN_ORM = 'postgresql+psycopg2://postgres:postgres@localhost:5432/bot'
engine_orm = sq.create_engine(DSN_ORM)
Session_orm = sessionmaker(bind=engine_orm)

session_orm = Session_orm()
Base = declarative_base()

with psycopg2.connect(user='ENTER YOUR USERNAME', password = 'ENTER YOUR PASSWORD') as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT 'CREATE DATABASE bot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bot')""")

class Users(Base):
    __tablename__ = 'users'
    
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_id_number = sq.Column(sq.Integer, unique=True, nullable=False)
    views_quantity = sq.Column(sq.Integer, nullable=False)
    favorites = relationship('Favorites', secondary = 'users_favorites')
    
class Users_Favorites(Base):
    __tablename__ = 'users_favorites'
    
    __table_args__ = (sq.PrimaryKeyConstraint('user_id', 'favorite_id'),)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    favorite_id = sq.Column(sq.Integer, sq.ForeignKey('favorites.id'))
    
class Favorites(Base):
    __tablename__ = 'favorites'
    
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    favorite_id_number = sq.Column(sq.Integer, unique=True, nullable=False)
    users = relationship('Users', secondary = 'users_favorites')
    
def create_tables(engine_orm):
    Base.metadata.drop_all(engine_orm)
    Base.metadata.create_all(engine_orm)
    
create_tables(engine_orm)
    