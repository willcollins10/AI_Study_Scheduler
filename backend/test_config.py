#test_config.py
class TestConfig:
    TESTING = True
    SQLAlCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False