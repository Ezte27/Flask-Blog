from flask import render_template, url_for, flash, redirect, request
from flaskBlog import app, bcrypt, db
from flaskBlog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskBlog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title="About")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        
        # Saving User
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! You are now able to login', 'success')

        return redirect(url_for('home'))

    return render_template('register.html', title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            

            if user.username == "admin":
                flash('Welcome Back Admin!', 'success')

            else:
                flash('You have been logged in!', 'success')

            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/imgs', picture_fn)

    output_size = (150, 150)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def delete_prev_picture(prev_picture_fn):

    if prev_picture_fn != "default.png":
        try:
            prev_picture_path = os.path.join(app.root_path, 'static/imgs', prev_picture_fn)

            os.remove(prev_picture_path)
        
        except FileNotFoundError:
            print(f"Warning! Previous image couldn't be deleted because the image was not found. prev_picture_path = {prev_picture_path}")

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.profile_pic.data:
            fn = save_picture(form.profile_pic.data)
            delete_prev_picture(current_user.image_file)
            current_user.image_file = fn

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename="imgs/" + current_user.image_file)

    return render_template('account.html', title="Account", profile_pic = image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", "success")
        return redirect(url_for('home'))

    return render_template('create_post.html', title="New Post", form = form)