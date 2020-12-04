from app import app
from models import db, User, Post, Tag, PostTag

db.drop_all()
db.create_all()

User.query.delete()
Post.query.delete()
Tag.query.delete()
PostTag.query.delete()

# add users
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

# add posts
titles = ("MASH", "Quote", "Dev")
contents = ("I very much so enjoyed starring in it", "Loneliness is everything it's cracked up to be", "I am an expert")
user_ids = (1, 1, 2)
posts = [Post(title=post[0], content=post[1], user_id=post[2]) for post in \
    zip(titles, contents, user_ids)]
db.session.add_all(posts)
db.session.commit()

# add tags
tag_names = ("funny", "very funny", "work", "profound")
tags = [Tag(name=name) for name in tag_names]
db.session.add_all(tags)
db.session.commit()

# create M2M relationships
posts_tags_ids = ((1, 1), (2, 1), (2, 2), (2, 4), (3, 3), (3, 4))
posts_tags = \
    [PostTag(post_id=post_tag_ids[0], tag_id=post_tag_ids[1]) \
    for post_tag_ids in posts_tags_ids]
db.session.add_all(posts_tags)
db.session.commit()

# for playing around only
def get_users():
    return User.query.all()