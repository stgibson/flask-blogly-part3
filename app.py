"""Blogly application."""

from flask import Flask, render_template, redirect, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag
from sqlalchemy import desc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "kubrick"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    """
        Shows the page not found page with a link back to the home page
        rtype: str
    """
    return render_template("404.html"), 404

@app.route("/")
def show_home_page():
    """
        Shows the home page with a list of 5 most recent posts
        rtype: str
    """
    posts = Post.query.order_by(desc(Post.created_at)).all()
    return render_template("home.html", posts=posts)

@app.route("/users")
def show_user_list():
    """
        Shows a list of all users, along with an option to add a new user. Each
        user's name is linked to the user's profile.
        rtype: str
    """
    users = User.query.order_by(User.last_name, User.first_name).all()

    return render_template("users.html", users=users)

@app.route("/users/new")
def show_add_user_form():
    """
        Shows a form the user can fill out and submit to add a new user
        rtype: str
    """
    return render_template("add-user.html")

@app.route("/users/new", methods=["POST"])
def add_new_user():
    """
        Adds a new user using the info submitted from the form by the user, and
        then redirects back to the users page
        rtype: str
    """
    # first get info from form
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    # validate user input (for now, first and last name are mandatory)
    if not first_name or not last_name:
        flash("Please fill out both your first name and your last name", \
            "danger")
        return redirect("/users/new")

    # add new user to db
    new_user = None
    if image_url:
        new_user = User(first_name=first_name, last_name=last_name, \
            image_url=image_url)
    else:
        new_user = User(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    flash("User has been successfully created", "success")
    return redirect("/users")

@app.route("/users/<int:user_id>")
def show_user_details(user_id):
    """
        Goes to a page that gives detail about the user with id user_id
        type user_id: int
        rtype: str
    """
    user = User.query.get_or_404(user_id)
    
    return render_template("user-details.html", user=user)

@app.route("/users/<int:user_id>/edit")
def show_user_edit_form(user_id):
    """
        Goes to the edit user page for the user with id user_id
        type user_id: int
        rtype: str
    """
    user = User.query.get_or_404(user_id)

    return render_template("edit-user.html", user=user)

@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """
        Edits details for the user with id user_id using info submitted from
        the form by the user, then redirects back to the users page
        type user_id: int
        rtype: str
    """
    # first get info from form
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    # verify first and last name
    if not first_name or not last_name:
        flash("Please fill out both your first name and your last name", \
            "danger")
        return redirect(f"/users/{user_id}/edit")

    # update the user in the db
    user = User.query.get(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url
    db.session.add(user)
    db.session.commit()

    flash("User has been successfully updated", "success")
    return redirect("/users")

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """
        Deletes user with id user_id, then redirects back to the users page
        type user_id: int
        rtype: str
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>/posts/new")
def show_add_post_form(user_id):
    """
        Shows a form the user can fill out and submit to create a new post
        type user_id: int
        rtype: str
    """
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template("add-post.html", user=user, tags=tags)

@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post(user_id):
    """
        Adds a new post for user with id user_id based on the info the user
        submitted in the form
        type user_id: int
        rtype: str
    """
    user = User.query.get(user_id)

    # get post details from form
    title = request.form["title"]
    content = request.form["content"]
    
    # get tags the user checked
    tags = Tag.query.all()
    tag_ids_selected = []
    for tag in tags:
        if request.form.get(tag.name, None):
            tag_ids_selected.append(tag.id)

    # verify user submitted both title and content
    if not title or not content:
        flash("Please fill out all fields", "danger")
        return redirect(f"/users/{user_id}/posts/new")

    # create post and add to db
    post = Post(title=title, content=content, user_id=user_id)
    db.session.add(post)
    db.session.commit()

    # add tags to post
    for tag_id in tag_ids_selected:
        post_tag = PostTag(post_id=post.id, tag_id=tag_id)
        db.session.add(post_tag)
    db.session.commit()

    flash("Post has been successfully created", "success")
    return redirect(f"/users/{user_id}")

@app.route("/posts/<int:post_id>")
def show_post_details(post_id):
    """
        Shows the title and content of post with id post_id, along with credits
        to the user who created the post, and options to go back to the user's
        page or to edit or delete the post
        type post_id: int
        rtype: str
    """
    post = Post.query.get_or_404(post_id)
    tags = post.tags

    return render_template("post-details.html", post=post, tags=tags)

@app.route("/posts/<int:post_id>/edit")
def show_post_edit_form(post_id):
    """
        Shows the form for the user to edit a post
        type post_id: int
        rtype: str
    """
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    post_tag_ids = [tag.id for tag in post.tags]

    return render_template("edit-post.html", post=post, tags=tags, \
        post_tag_ids=post_tag_ids)

@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post(post_id):
    """
        Edits post with id post_id using info user submitted in the form
        type post_id: int
        rtype: str
    """
    # get info submitted in form
    title = request.form["title"]
    content = request.form["content"]

    # verify the user entered both title and content
    if not title or not content:
        flash("Please fill out all fields", "danger")
        return redirect(f"/posts/{post_id}/edit")

    # edit post
    post = Post.query.get(post_id)
    post.title = title
    post.content = content
    db.session.add(post)
    db.session.commit()

    # update tags for post
    tags = Tag.query.all()
    post_tags = post.tags
    for tag in tags:
        # if checked and wasn't checked before, add tag to post
        if request.form.get(tag.name, None):
            tag_added = True
            for post_tag in post_tags:
                # if post already had tag, tag was not added
                if tag.id == post_tag.id:
                    tag_added = False
            if tag_added:
                post_tag = PostTag(post_id=post.id, tag_id=tag.id)
                db.session.add(post_tag)
        # if not checked and was before, remove tag from post
        else:
            tag_removed = False
            for post_tag in post_tags:
                # if post used to have tag, tag was removed
                if tag.id == post_tag.id:
                    tag_removed = True
            if tag_removed:
                post_tag = PostTag.query.filter_by(post_id=post.id, tag_id=tag.id).one()
                db.session.delete(post_tag)
    db.session.commit()

    flash("Post has been successfully updated", "success")
    return redirect(f"/posts/{post_id}")

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """
        Deletes post with id post_id
        type post_id: int
        rtype: str
    """
    # first determine which user created the post, to go to the user's page
    user = Post.query.get_or_404(post_id).user
    post = Post.query.filter_by(id=post_id).one()
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route("/tags")
def show_tag_list():
    """
        Shows list of tags with a link back to the home page and a link to add
        a new tag
        rtype: str
    """
    tags = Tag.query.all()

    return render_template("tags.html", tags=tags)

@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    """
        Shows the details of tag with id tag_id, along with a list of posts
        with the tag, and links to edit or delete the post and to go back to
        the list of posts
        type tag_id: int
        rtype: str
    """
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts

    return render_template("tag-details.html", tag=tag, posts=posts)

@app.route("/tags/new")
def show_add_tag_form():
    """
        Shows the form to add a new tag
        rtype: str
    """
    return render_template("add-tag.html")

@app.route("/tags/new", methods=["POST"])
def add_tag():
    """
        Adds a new tag using the info the user submitted in the form
        rtype: str
    """
    # first get the user's submitted info
    name = request.form["name"]
    # verify the user typed in a name
    if not name:
        flash("Please enter a name for the tag", "danger")
        return redirect("/tags/new")
    
    # add the new tag to db
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()

    flash("The tag has been successfully created", "success")
    return redirect("/tags")

@app.route("/tags/<int:tag_id>/edit")
def show_edit_tag_form(tag_id):
    """
        Shows the form to edit tag with id tag_id
        type tag_id: int
        rtype: str
    """
    tag = Tag.query.get_or_404(tag_id)

    return render_template("edit-tag.html", tag=tag)

@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def edit_tag(tag_id):
    """
        Edits the tag with id tag_id using the info the user submitted in the
        form
        type tag_id: int
        rtype: str
    """
    # first get the info submitted by the user
    name = request.form["name"]
    # verify the user submitted a name
    if not name:
        flash("Please enter a name for the tag", "danger")
        return redirect(f"/tags/{tag_id}/edit")

    # edit the tag
    tag = Tag.query.get_or_404(tag_id)
    tag.name = name
    db.session.add(tag)
    db.session.commit()

    flash("The tag has been successfully edited", "success")
    return redirect("/tags")

@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """
        Deletes the tag with id tag_id
        type tag_id: int
        rtype: str
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")