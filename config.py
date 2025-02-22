import os


base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    GMAIL_USER_EMAIL = os.environ.get("GMAIL_USER_EMAIL")
    GMAIL_PASSWORD = os.environ.get("GMAIL_USER_PASSWORD")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") 
    FLASK_APP = os.environ.get("FLASK_APP")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(base_dir, 'blog.db')
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
    ENV = os.environ.get("ENV")