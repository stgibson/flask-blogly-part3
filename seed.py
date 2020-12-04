from app import app
from models import db, User, Post

db.drop_all()
db.create_all()

User.query.delete()
Post.query.delete()

first_names = ("Alan", "Joel", "Jane")
last_names = ("Alda", "Burton", "Smith")
image_urls = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Alan_Alda_circa_1960s.JPG/800px-Alan_Alda_circa_1960s.JPG",
    "",
    ""
)
users = [User(first_name=user[0], last_name=user[1], image_url=user[2]) \
    for user in zip(first_names, last_names, image_urls)]

db.session.add_all(users)
db.session.commit()

titles = ("MASH", "Quote", "Dev")
contents = ("I very much so enjoyed starring in it", "Loneliness is everything it's cracked up to be", "I am an expert")
user_ids = (1, 1, 2)
posts = [Post(title=post[0], content=post[1], user_id=post[2]) for post in \
    zip(titles, contents, user_ids)]

db.session.add_all(posts)
db.session.commit()