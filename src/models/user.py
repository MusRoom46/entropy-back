from config.db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_encrypted = db.Column(db.LargeBinary, nullable=False)
    entropy = db.Column(db.Float, nullable=False)
    role = db.Column(db.String(5), nullable=False, default="user") # "user" ou "admin"

    def __repr__(self):
        return f"<User {self.username}>"
