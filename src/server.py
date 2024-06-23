from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, validators, IntegerField, URLField
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, desc
import requests
from datetime import datetime, date


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class = Base)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = "xxxx"
db.init_app(app)
 

class Blog(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String(250), unique = True, nullable = False)
    sub_title: Mapped[str] = mapped_column(String(250))
    date: Mapped[int] = mapped_column(String(250), unique = False)
    editor: Mapped[str] = mapped_column(String(250), unique = False)
    content: Mapped[str] = mapped_column(String(10000))
    img_url: Mapped[str] = mapped_column(String(1000))


class Project(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String(250), unique = True, nullable = False)
    description: Mapped[str] = mapped_column(String(250))
    github: Mapped[str] = mapped_column(String(1000))
    website: Mapped[str] = mapped_column(String(1000), nullable = True)
    status: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


class BlogForm(FlaskForm):
    title = StringField(
        label = "Blog Title: ",
        validators = [
            validators.DataRequired(message = "Please Enter a Blog Title")
        ]
    )
    sub_title = StringField(label = "Blog Sub-Title: ")
    editor = StringField(label = "Editor: ")
    content = CKEditorField(
        label = "Blog Content: ",
        validators = [
            validators.DataRequired(message = "Please Enter Blog Content")
        ]
    )
    img_url = URLField(label = "Blog Image: ")
    submit = SubmitField(label = "Add Blog Post")


class EditBlogForm(FlaskForm):
    content = CKEditorField(
        label = "Blog Content: ",
        validators = [
            validators.DataRequired(message = "Please Enter Blog Content")
        ]
    )
    img_url = URLField(label = "Blog Image: ")
    submit = SubmitField(label = "Edit Blog Post")


class ProjectForm(FlaskForm):
    title = StringField(
        label = "Project Title: ",
        validators = [
            validators.DataRequired(message = "Please Enter a Project Title")
        ]
    )
    description = StringField(label = "Project Description: ")
    github = URLField(label = "Project Repo: ")
    website = URLField(label = "Website URL: ")
    status = StringField(label = "Project Status: ")
    submit = SubmitField(label = "Add Project")


class EditProjectForm(FlaskForm):
    title = StringField(
        label = "Project Title: ",
        validators = [
            validators.DataRequired(message = "Please Enter a Project Title")
        ]
    )
    description = StringField(label = "Project Description: ")
    github = URLField(label = "Project Repo: ")
    website = URLField(label = "Website URL: ")
    status = StringField(label = "Project Status: ")
    submit = SubmitField(label = "Edit Project")


@app.route("/")
def index():
    return(render_template(
        "index.html"  
    ))


@app.route("/about")
def about():
    return(render_template(
        "about.html"  
    ))


@app.route("/resume")
def resume():
    return(render_template(
        "resume.html"  
    ))

@app.route("/gallery")
def gallery():
    return(render_template(
        "gallery.html"  
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
                "editor": row[0].editor,
                "content": row[0].content,
                "img_url": row[0].img_url
            } for row in blog_posts
        ]
        n_blogs = len(blogs)
    return(render_template(
        "blogs.html",
        blogs = blogs,
        n_blogs = n_blogs
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
        n_projects = n_projects
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
                "editor": blog.editor,
                "content": blog.content,
                "img_url": blog.img_url
            }
    return(render_template(
        "get_blog.html",
        blog = blog
    ))


@app.route("/blogs/edit", methods = ["GET", "POST"])
def edit_blog():
    blog_id = request.args.get("blog_id")
    form = EditBlogForm()
    if form.validate_on_submit():
        with app.app_context():
            blog =  db.session.execute(db.select(Blog).where(Blog.id==blog_id)).scalar()
            blog.content = form.content.data
            blog.img_url = form.img_url.data
            db.session.commit()
        return(redirect(url_for("get_blog", blog_id=blog_id)))
    return(render_template(
        "edit_blog.html",
        form = form,
        blog_id = blog_id
    ))


@app.route("/blogs/delete", methods = ["GET", "POST"])
def delete_blog():
    blog_id = request.args.get("blog_id")
    with app.app_context():
        blog =  db.session.execute(db.select(Blog).where(Blog.id==blog_id)).scalar()
        db.session.delete(blog)
        db.session.commit()
        return(redirect(url_for("blogs")))


@app.route("/add_blog", methods = ["GET", "POST"])
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
        form = form
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
        project = project
    ))


@app.route("/projects/edit", methods = ["GET", "POST"])
def edit_project():
    project_id = request.args.get("project_id")
    form = EditProjectForm()
    with app.app_context():
        project =  db.session.execute(db.select(Project).where(Project.id==project_id)).scalar()
        original_project = project.title
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
        original_project = original_project
    ))


@app.route("/projects/delete", methods = ["GET", "POST"])
def delete_project():
    project_id = request.args.get("project_id")
    with app.app_context():
        project =  db.session.execute(db.select(Project).where(Project.id==project_id)).scalar()
        db.session.delete(project)
        db.session.commit()
        return(redirect(url_for("projects")))


@app.route("/add_project", methods = ["GET", "POST"])
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
        form = form
    ))
        

if __name__ == "__main__":
    app.run(debug = True)


