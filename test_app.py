from unittest import TestCase
from app import app
from models import db, User, Post

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly_test"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["TESTING"] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

db.drop_all()
db.create_all()

base_url = "http://localhost"

class UserViewsTestCase(TestCase):
    """
        Tests for views for Users.
    """
    def setUp(self):
        """
            Adds test users and posts to test db
        """
        Post.query.delete()
        User.query.delete()
        db.session.commit()

        # add users
        num_of_users = 3
        first_names = ("Alan", "Joel", "Jane")
        last_names = ("Alda", "Burton", "Smith")
        image_urls = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Alan_Alda_circa_1960s.JPG/800px-Alan_Alda_circa_1960s.JPG",
            "",
            ""
        )
        users = [
            User(first_name=user[0], last_name=user[1], image_url=user[2]) \
                for user in zip(first_names, last_names, image_urls)
        ]
        db.session.add_all(users)
        db.session.commit()

        # save info on users
        self.num_of_users = num_of_users
        self.first_names = first_names
        self.last_names = last_names
        self.image_urls = image_urls
        self.users = users

        # add posts
        num_of_posts = 3
        titles = ("MASH", "Quote", "Dev")
        # changed 2nd quote from it's to its to avoid issue with rendering '
        contents = (
            "I very much so enjoyed starring in it",
            "Loneliness is everything it is cracked up to be",
            "I am an expert"
        )
        user_ids = (
            User.query.filter_by(first_name=first_names[0]).one().id,
            User.query.filter_by(first_name=first_names[0]).one().id,
            User.query.filter_by(first_name=first_names[1]).one().id
        )
        posts = [
            Post(title=post[0], content=post[1], user_id=post[2]) \
                for post in zip(titles, contents, user_ids)
        ]
        db.session.add_all(posts)
        db.session.commit()
        
        # save info on posts
        self.num_of_posts = num_of_posts
        self.titles = titles
        self.contents = contents
        self.user_ids = user_ids
        self.posts = posts

    def tearDown(self):
        """
            Undoes any failed transactions
        """
        db.session.rollback()
    
    # TODO: need to update this test
    def test_show_home_page(self):
        """
            Tests show_home_page() shows posts
        """
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            for i in range(self.num_of_posts):
                test_post = Post.query.filter_by(title=self.titles[i]).one()
                test_user = User.query.get(test_post.user_id)
                self.assertIn(test_post.title, html)
                self.assertIn(test_post.content, html)
                self.assertIn(test_user.full_name, html)

    def test_show_user_list(self):
        """
            Tests show_user_list() renders users.html correctly with the users'
            names and correct links
        """
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            for user in self.users:
                self.assertIn(f"/users/{user.id}", html)
                self.assertIn(f"{user.first_name} {user.last_name}", html)

    def test_add_new_user(self):
        """
            Tests add_new_user() correctly adds user to db and redirects
        """
        with app.test_client() as client:
            first_name = "Sean"
            last_name = "Gibson"
            data = {
                "first-name": first_name,
                "last-name": last_name,
                "image-url": ""
            }
            resp = client.post("/users/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{first_name} {last_name}", html)

    def test_show_user_details(self):
        """
            Tests show_user_details(user_id) renders user info correctly
        """
        with app.test_client() as client:
            for i in range(self.num_of_users):
                test_user = User.query.filter_by(
                    first_name=self.first_names[i]
                ).one()
                user_id = test_user.id
                resp = client.get(f"/users/{user_id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(test_user.full_name, html)
                if self.image_urls[i]:
                    self.assertIn(test_user.image_url, html)
                else:
                    self.assertIn("/static/placeholder.jpg", html)

                # also test is showing user's posts
                posts = Post.query.filter_by(user_id=test_user.id).all()
                for post in posts:
                    self.assertIn(post.title, html)
                    self.assertIn(f"/posts/{post.id}", html)

    def test_user_edit_form(self):
        """
            Tests user_edit_form(user_id) shows user edit form correct user
            info in inputs
        """
        with app.test_client() as client:
            for i in range(self.num_of_users):
                test_user = User.query.filter_by(
                    first_name=self.first_names[i]
                ).one()
            resp = client.get(f"/users/{test_user.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(test_user.first_name, html)
            self.assertIn(test_user.last_name, html)
            self.assertIn(test_user.image_url, html)

    def test_edit_user(self):
        """
            Tests edit_user(user_id) updates user info and redirects to user
            details page correctly
        """
        with app.test_client() as client:
            new_first_name = "Sean"
            new_last_name = "Gibson"
            new_image_url = ""
            data = {
                "first-name": new_first_name,
                "last-name": new_last_name,
                "image-url": new_image_url
            }
            test_user = User.query.filter_by(
                first_name=self.first_names[0]
            ).one()
            user_id = test_user.id
            resp = client.post(f"/users/{user_id}/edit", data=data, \
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{new_first_name} {new_last_name}", html)

    def test_delete_user(self):
        """
            Tests delete_user(user_id) successfully deletes user info and
            redirects to user listing page correctly, where the user should no
            longer appear
        """
        with app.test_client() as client:
            test_user = \
                User.query.filter_by(first_name=self.first_names[2]).one()
            resp = client.post(f"/users/{test_user.id}/delete", \
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(test_user.full_name, html)

            # make sure other users weren't also deleted
            other_users = \
                User.query.filter(User.first_name != self.first_names[2]).all()
            for user in other_users:
                self.assertIn(user.full_name, html)

    def test_add_post(self):
        """
            Tests add_post(user_id) creates a new post correctly
        """
        with app.test_client() as client:
            new_title = "Comedy"
            new_content = "It's easier than tragedy"
            data = {
                "title": new_title,
                "content": new_content
            }
            test_user = \
                User.query.filter_by(first_name=self.first_names[0]).one()
            resp = client.post(f"/users/{test_user.id}/posts/new", data=data, \
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(new_title, html)

    def test_show_post_details(self):
        """
            Tests show_post_details(post_id) shows correct post info
        """
        with app.test_client() as client:
            for i in range(self.num_of_posts):
                test_post = Post.query.filter_by(title=self.titles[i]).one()
                test_user = User.query.get(test_post.user_id)
                resp = client.get(f"/posts/{test_post.id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(test_post.title, html)
                self.assertIn(test_post.content, html)
                self.assertIn(f"By {test_user.full_name}", html)

    def test_show_post_edit_form(self):
        """
            Tests show_post_edit_form(post_id) shows edit post form with
            correct info on the post filled in
        """
        with app.test_client() as client:
            for i in range(self.num_of_posts):
                test_post = Post.query.filter_by(title=self.titles[i]).one()
                resp = client.get(f"/posts/{test_post.id}/edit")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(test_post.title, html)
                self.assertIn(test_post.content, html)

    def test_edit_post(self):
        """
            Tests edit_post(post_id) edits post correctly and redirects to user
            details page, which shows the updated title of the post
        """
        with app.test_client() as client:
            new_title = "M.A.S.H"
            new_content = "I enjoyed playing Hawkeye"
            data = {
                "title": new_title,
                "content": new_content
            }
            test_post = Post.query.filter_by(title=self.titles[0]).one()
            resp = client.post(f"/posts/{test_post.id}/edit", data=data, \
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(new_title, html)

    def test_delete_post(self):
        """
            Tests delete_post(post_id) deletes post correctly and redirects to
            user details page with the post no longer showing up
        """
        with app.test_client() as client:
            test_post = Post.query.filter_by(title=self.titles[0]).one()
            test_user = User.query.filter_by(id=test_post.user_id)
            resp = client.post(f"/posts/{test_post.id}/delete", \
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(test_post.title, html)

            # verify that the user's other posts have not been deleted
            other_posts = \
                Post.query.filter((Post.user_id == test_post.user_id) & \
                    (Post.title != test_post.title)).all()
            for post in other_posts:
                self.assertIn(post.title, html)