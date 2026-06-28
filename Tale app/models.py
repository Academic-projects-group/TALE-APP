from extensions import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from datetime import datetime

db = SQLAlchemy()
# Association table for followers
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)    
# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50), unique=True, nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stories = db.relationship('Story', backref='author', lazy=True)  
    profile_pic = db.Column(db.String(255), default='default.jpg')
    private_account = db.Column(db.Boolean, default=False)  # Ensure this line is present
    # Many-to-Many Self-Referential Relationship
    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_following(self, user):
        """Check if the current user is following another user."""
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        """Follow another user."""
        if not self.is_following(user):
            self.following.append(user)
            db.session.commit()

    def unfollow(self, user):
        """Unfollow a user."""
        if self.is_following(user):
            self.following.remove(user)
            db.session.commit()


    def like_story(self, story):
        if not self.has_liked_story(story):
            self.liked_stories.append(story)

    def unlike_story(self, story):
        if self.has_liked_story(story):
            self.liked_stories.remove(story)

    def has_liked_story(self, story):
        return self.liked_stories.filter(story_likes.c.story_id == story.id).count() > 0


# Association table for story likes
story_likes = db.Table('story_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('story_id', db.Integer, db.ForeignKey('story.id'), primary_key=True)
)

'''class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='stories')
    likes = db.relationship('User', secondary=story_likes, backref=db.backref('liked_stories', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign Key
    author = db.relationship('User', backref='user_stories')'''
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('stories', lazy=True))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    story = db.relationship('Story', backref=db.backref('comments', lazy=True))

    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meme_id = db.Column(db.Integer, db.ForeignKey('meme.id'), nullable=False)

    def __repr__(self):
        return f"<Comment {self.username}: {self.content}>"
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # Ensure title exists
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # Store the file path
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  # Import the db instance from app.py




class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shares = db.Column(db.Integer, default=0)  # ✅ Fix: Ensure column exists
    image_path = db.Column(db.String(255), nullable=False)
    likes = db.relationship("Like", backref="meme", lazy=True)
    comments = db.relationship("Comment", backref="meme", lazy=True)

    def like_count(self):
        return len(self.likes)

    def comment_count(self):
        return len(self.comments)

    user = db.relationship('User', backref=db.backref('memes', lazy=True))

# Like model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('user.uname'), nullable=False)
    meme_id = db.Column(db.Integer, db.ForeignKey('meme.id'), nullable=False)
