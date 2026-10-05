from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "it-news-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Сначала войдите в аккаунт"

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)


class Author(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile = db.relationship("Profile", backref="author", uselist=False)
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    about = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), unique=True, nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    comments = db.relationship("Comment", backref="post")
    tags = db.relationship("Tag", secondary=post_tags, backref="posts")


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Author, int(user_id))


def get_tags(text):
    names = {name.strip().lower() for name in text.split(",") if name.strip()}
    return [Tag.query.filter_by(name=name).first() or Tag(name=name) for name in names]


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "")
    posts = Post.query.order_by(Post.created_at.desc())
    if q:
        posts = posts.filter(Post.title.ilike(f"%{q}%") | Post.text.ilike(f"%{q}%"))
    if tag:
        posts = posts.filter(Post.tags.any(Tag.name == tag))
    return render_template("index.html", posts=posts.all(), q=q, tag=tag)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template("post.html", post=post)


@app.route("/author/<username>")
def author_page(username):
    author = Author.query.filter_by(username=username).first_or_404()
    return render_template("author.html", author=author)


@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = db.get_or_404(Post, post_id)
    text = request.form["text"].strip()
    if text:
        db.session.add(Comment(text=text, post_id=post.id, author_id=current_user.id))
        db.session.commit()
    else:
        flash("Комментарий не может быть пустым")
    return redirect(url_for("show_post", post_id=post.id))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form["title"].strip()
        text = request.form["text"].strip()
        if not title or not text:
            flash("Заполните заголовок и текст")
        else:
            post = Post(title=title, text=text, author_id=current_user.id)
            post.tags = get_tags(request.form.get("tags", ""))
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
    return render_template("new_post.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Заполните логин и пароль")
        elif Author.query.filter_by(username=username).first():
            flash("Такой логин уже занят")
        else:
            author = Author(username=username)
            author.set_password(password)
            author.profile = Profile(
                full_name=request.form.get("full_name", "").strip(),
                about=request.form.get("about", "").strip(),
            )
            db.session.add(author)
            db.session.commit()
            login_user(author)
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        author = Author.query.filter_by(username=request.form["username"]).first()
        if author and author.check_password(request.form["password"]):
            login_user(author)
            return redirect(url_for("index"))
        flash("Неверный логин или пароль")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
