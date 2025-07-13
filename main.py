# Import libraries
from flask import Flask, render_template, url_for, request, redirect, flash, get_flashed_messages, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, desc
import requests
from datetime import datetime, date
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
import uuid
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import logging
from logging.handlers import RotatingFileHandler


# Import modules
from config import Config
from forms import BlogForm, EditBlogForm, ProjectForm, EditProjectForm, AddImageForm, ContactForm, LoginForm, RegisterForm, EditAboutForm


load_dotenv()


class Base(DeclarativeBase):
    pass


# Configurations
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy(model_class = Base)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)
if Config.ENV == "dev":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["UPLOAD_FOLDER"] = "static/images/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
app.config['CKEDITOR_PKG_TYPE'] = 'full'
app.config['RECAPTCHA_PUBLIC_KEY'] = Config.RECAPTCHA_SITE_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = Config.RECAPTCHA_SECRET_KEY
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


class Blog(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String(250), unique = True, nullable = False)
    sub_title: Mapped[str] = mapped_column(String(250))
    date: Mapped[int] = mapped_column(String(250), unique = False)
    editor: Mapped[str] = mapped_column(String(250), unique = False)
    content: Mapped[str] = mapped_column(String(100000))
    img_url: Mapped[str] = mapped_column(String(1000))


class Project(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String(250), unique = True, nullable = False)
    description: Mapped[str] = mapped_column(String(250))
    github: Mapped[str] = mapped_column(String(1000))
    website: Mapped[str] = mapped_column(String(1000), nullable = True)
    status: Mapped[str] = mapped_column(String(1000))


class Image(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String(500), nullable = True)
    image: Mapped[str] = mapped_column(String(500), unique = True, nullable = False)


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    email: Mapped[str] = mapped_column(String(100), unique = True)
    password: Mapped[str] = mapped_column(String(100))


class About(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    about_me: Mapped[str] = mapped_column(String(10000), unique = True)


@login_manager.user_loader
def load_user(user_id):
    return(db.get_or_404(User, user_id))


with app.app_context():
    db.create_all()


@app.route("/sitemap.xml")
def sitemap():
    return(send_from_directory(app.root_path, "sitemap.xml"))


@app.route("/")
def index():
    print(current_user.is_authenticated)
    return(render_template(
        "index.html",
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/about")
def about():
    about =  db.session.execute(db.select(About)).scalars().first()
    print(about)
    return(render_template(
        "about.html",
        is_authenticated = current_user.is_authenticated,
        about = about
    ))


@app.route("/about/edit", methods = ["GET", "POST"])
@login_required
def edit_about():
    with app.app_context():
        about =  db.session.execute(db.select(About)).scalars().first()
        print(about)
        if about and about is not None:
            form = EditAboutForm(
                about_me = about.about_me 
            )
        else:
            default_about = About(
                about_me = ""
            )
            db.session.add(default_about)
            db.session.commit()
            form = EditAboutForm()
        if form.validate_on_submit():
            about.about_me = form.about_me.data
            db.session.commit()
            return(redirect(url_for("about")))
    return(render_template(
        "edit_about.html",
        form = form,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/resume")
def resume():
    return(render_template(
        "resume_v2.html",
        is_authenticated = current_user.is_authenticated  
    ))


@app.route("/blogs")
def blogs():
    with app.app_context():
        blog_posts = db.session.execute(
            db.select(Blog).order_by(desc(Blog.date))
        ).fetchall()
        blogs = [
            {
                "id": row[0].id,
                "title": row[0].title, 
                "sub_title": row[0].sub_title, 
                "date": row[0].date,
                "month": datetime.strptime(row[0].date, "%Y-%m-%d").strftime("%B"),
                "day": datetime.strptime(row[0].date, "%Y-%m-%d").day,
                "year": datetime.strptime(row[0].date, "%Y-%m-%d").year,
                "editor": row[0].editor,
                "content": row[0].content,
                "img_url": row[0].img_url
            } for row in blog_posts
        ]
        n_blogs = len(blogs)
    return(render_template(
        "blogs.html",
        blogs = blogs,
        n_blogs = n_blogs,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/projects")
def projects():
    with app.app_context():
        projects = db.session.execute(
            db.select(Project).order_by((Project.id))
        ).fetchall()
        projects = [
            {
                "id": row[0].id,
                "title": row[0].title, 
                "description": row[0].description, 
                "github": row[0].github,
                "website": row[0].website,
                "status": row[0].status
            } for row in projects
        ]
        n_projects = len(projects)
    return(render_template(
        "projects.html",
        projects = projects,
        n_projects = n_projects,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/gallery")
def gallery():
    with app.app_context():
        images = db.session.execute(
            db.select(Image).order_by(desc(Image.id))
        ).fetchall()
        images = [
            {
                "id": row[0].id,
                "image": row[0].image.split("static/")[1],
                "title": row[0].title, 
            } for row in images
        ]
        n_images = len(images)
        print([image["image"] for image in images])
    return(render_template(
        "gallery.html",
        images = images,
        n_images = n_images,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/contact", methods = ["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        conn = smtplib.SMTP("smtp.gmail.com")
        my_email = os.getenv("GMAIL_USER_EMAIL")
        my_password = os.getenv("GMAIL_APP_PASSWORD")
        message = EmailMessage()
        message["From"] = my_email
        message["To"] = my_email
        message["subject"] = f"""{form.name.data} ({form.email.data}) has reached out from your website."""
        message.set_content(form.message.data)
        conn.starttls()
        conn.login(
            user = my_email,
            password = my_password
        )
        conn.send_message(message)
        conn.close()
        return(redirect(url_for("contact")))
    return(render_template(
        "contact.html",
        form = form,
        is_authenticated = current_user.is_authenticated,
        recaptcha_site_key = os.getenv("RECAPTCHA_SITE_KEY")
    ))


@app.route("/blogs/<int:blog_id>")
def get_blog(blog_id):
    with app.app_context():
        blog =  db.session.execute(db.select(Blog).where(Blog.id==blog_id)).scalar()
        if blog == None:
            return("Blog not found :/", 404)
        else:
            blog = {
                "id": blog.id,
                "title": blog.title, 
                "sub_title": blog.sub_title, 
                "date": blog.date,
                "month": datetime.strptime(blog.date, "%Y-%m-%d").strftime("%B"),
                "day": datetime.strptime(blog.date, "%Y-%m-%d").day,
                "year": datetime.strptime(blog.date, "%Y-%m-%d").year,
                "editor": blog.editor,
                "content": blog.content,
                "img_url": blog.img_url
            }
    return(render_template(
        "get_blog.html",
        blog = blog,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/blogs/edit", methods = ["GET", "POST"])
@login_required
def edit_blog():
    with app.app_context():
        blog_id = request.args.get("blog_id")
        blog =  db.session.execute(db.select(Blog).where(Blog.id==blog_id)).scalar()
        form = EditBlogForm(
            title = blog.title,
            sub_title=blog.sub_title,
            content=blog.content,
            img_url=blog.img_url
        )
        if form.validate_on_submit():
            blog.title = form.title.data
            blog.sub_title = form.sub_title.data
            blog.content = form.content.data
            blog.img_url = form.img_url.data
            db.session.commit()
            return(redirect(url_for("get_blog", blog_id=blog_id)))
    return(render_template(
        "edit_blog.html",
        form = form,
        blog_id = blog_id,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/blogs/delete", methods = ["GET", "POST"])
@login_required
def delete_blog():
    blog_id = request.args.get("blog_id")
    with app.app_context():
        blog =  db.session.execute(db.select(Blog).where(Blog.id==blog_id)).scalar()
        db.session.delete(blog)
        db.session.commit()
        return(redirect(url_for("blogs")))


@app.route("/add_blog", methods = ["GET", "POST"])
@login_required
def add_blog():
    form = BlogForm()
    if form.validate_on_submit():
        new_blog = Blog(
            title = form.title.data,
            sub_title = form.sub_title.data,
            date = datetime.strftime(datetime.now(), format = "%Y-%m-%d"),
            editor = form.editor.data,
            content = form.content.data,
            img_url = form.img_url.data
        )
        db.session.add(new_blog)
        db.session.commit()
        return(redirect(url_for("blogs")))
    return(render_template(
        "add_blog.html",
        form = form,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/projects/<int:project_id>")
def get_project(project_id):
    with app.app_context():
        project =  db.session.execute(db.select(Project).where(Project.id==project_id)).scalar()
        if project == None:
            return("Project not found :/", 404)
        else:
            project = {
                "id": project.id,
                "title": project.title, 
                "description": project.description, 
                "github": project.github,
                "website": project.website,
                "status": project.status
            }
    return(render_template(
        "get_project.html",
        project = project,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/projects/edit", methods = ["GET", "POST"])
@login_required
def edit_project():
    project_id = request.args.get("project_id")
    with app.app_context():
        project =  db.session.execute(db.select(Project).where(Project.id==project_id)).scalar()
        original_project = project.title
        form = EditProjectForm(
            title = project.title,
            description = project.description,
            github = project.github,
            website = project.website,
            status = project.status
        )
        if form.validate_on_submit():
            project.title = form.title.data
            project.description = form.description.data
            project.github = form.github.data
            project.website = form.website.data
            project.status = form.status.data
            db.session.commit()
            return(redirect(url_for("projects")))
    return(render_template(
        "edit_project.html",
        form = form,
        project_id = project_id,
        original_project = original_project,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/projects/delete", methods = ["GET", "POST"])
@login_required
def delete_project():
    project_id = request.args.get("project_id")
    with app.app_context():
        project =  db.session.execute(db.select(Project).where(Project.id==project_id)).scalar()
        db.session.delete(project)
        db.session.commit()
        return(redirect(url_for("projects")))


@app.route("/add_project", methods = ["GET", "POST"])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            title = form.title.data,
            description = form.description.data,
            github = form.github.data,
            website = form.website.data,
            status = form.status.data
        )
        db.session.add(new_project)
        db.session.commit()
        return(redirect(url_for("projects")))
    return(render_template(
        "add_project.html",
        form = form,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/gallery/add_image", methods = ["GET", "POST"])
@login_required
def add_image():
    form = AddImageForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(file_path)
            new_image = Image(
                image = file_path,
                title = form.title.data
            )
            db.session.add(new_image)
            db.session.commit()
            return(redirect(url_for("gallery")))
    return(render_template(
        "add_image.html",
        form = form,
        is_authenticated = current_user.is_authenticated
    ))


# Redundant after intial registration
'''
@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        hash_password = generate_password_hash(
            form.password.data,
            method = "pbkdf2:sha256",
            salt_length = 8
        )
        with app.app_context():
            user = db.session.execute(
                db.select(User).where(User.email == email)
            ).scalar()
            if user:
                flash("Email alread exists in database")
            else:
                new_user = User(
                    email = email,
                    password = hash_password
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return(redirect(url_for("index")))
    else:
        return(render_template(
            "register.html",
            form = form,
            is_authenticated = current_user.is_authenticated
        ))
'''


@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        with app.app_context():
            user = db.session.execute(
                db.select(User).where(User.email == email)
            ).scalar()
            if user:
                if check_password_hash(user.password, password = form.password.data):
                    login_user(user)
                    return(redirect(url_for('index')))
                else:
                    flash("Invalid credentials")
            else:
                flash("Invalid credentials")
    return(render_template(
        "login.html",
        form = form,
        is_authenticated = current_user.is_authenticated
    ))


@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for("index")))


if __name__ == "__main__":
    app.run(debug = False)


