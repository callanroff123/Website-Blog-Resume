# Import libraries to build and automate web forms
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, validators, IntegerField, URLField, FileField, EmailField, PasswordField
from flask_ckeditor import CKEditor, CKEditorField


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
    title = StringField(
        label = "Blog Title: ",
        validators = [
            validators.DataRequired(message = "Please Enter a Blog Title")
        ]
    )
    sub_title = StringField(label = "Blog Sub-Title: ")
    content = CKEditorField(
        label = "Blog Content: ",
        validators = [
            validators.DataRequired(message = "Please Enter Blog Content")
        ]
    )
    img_url = URLField(label = "Blog Image: ")
    submit = SubmitField(label = "Edit Blog Post")
    def __init__(self, original_blog = None, *args, **kwargs):
        super(EditBlogForm, self).__init__(*args, **kwargs)
        if original_blog:
            self.title.render_kw = {"placeholder": original_blog}


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


class AddImageForm(FlaskForm):
    title = StringField(label = "Image Title: ")
    image = FileField(label = "Image: ")
    submit = SubmitField(label = "Add Image")


class ContactForm(FlaskForm):
    name = StringField(
        label = "Name: ",
        validators = [validators.DataRequired(message = "Please Enter this Field.")]
    )
    email = EmailField(label = "Email: ")
    message = CKEditorField(
        label = "Message: ",
        validators = [validators.DataRequired(message = "Please Enter this Field.")],
            
    )
    submit = SubmitField(label = "Send")


class LoginForm(FlaskForm):
    email = EmailField(label = "Email: ")
    password = PasswordField(label = "Password: ")
    submit = SubmitField(label = "Login")


class RegisterForm(FlaskForm):
    email = EmailField(label = "Email: ")
    password = PasswordField(label = "Password: ")
    submit = SubmitField(label = "Register")