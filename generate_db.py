from app import db
from app import app

if __name__ == "__main__":
    with app.test_request_context():
        db.create_all()
