from dotenv import load_dotenv
import redis
import os

load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:8000/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ["SECRET_KEY"]
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")



