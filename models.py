"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """
        Schema for the users table in the db. Contains id, the user's first and
        last name and a url to an image of the user's profile.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    first_name = db.Column(db.Text, nullable=False)
    
    last_name = db.Column(db.Text, nullable=False)
    
    image_url = db.Column(db.Text)

    posts = db.relationship("Post", backref="user", \
        cascade="all, delete-orphan")

    @property
    def full_name(self):
        """
            Gets the user's first and last name concatenated. This way, if
            the format for names changes, the update only needs to be reflected
            in this method.
            rtype: str
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return \
            f"<User id={self.id} first_name={self.first_name} last_name={self.last_name} image_url={self.image_url or None}>"

class Post(db.Model):
    """
        Schema for the posts table in the db. Contains id, the title for the
        post, the post's content, the date and time the post was created, and
        a reference to the user who created the post
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text, nullable=False)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @property
    def friendly_date(self):
        """
            Gets the date and time the post was created in a more casaul form.
        """
        return self.created_at.strftime("%a %b %#d %Y, %#I:%M %p")

    def __repr__(self):
        return \
            f"<Post id={self.id} title={self.title} content={self.content} created_at={self.created_at} user_id={self.user_id}>"