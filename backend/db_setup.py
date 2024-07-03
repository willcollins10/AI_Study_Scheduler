from app import app, db

with app.app_context():
    # Drop all existing database tables
    db.drop_all()
    # Create new databse tables
    db.create_all()
    print("Database tables created.")
