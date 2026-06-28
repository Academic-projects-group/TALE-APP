from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import secrets
from flask import current_app
from PIL import Image  # Optional: to resize the image if needed
from extensions import db
# Import the form class
from forms import EditProfileForm
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime  # ✅ Correct way
from sqlalchemy.orm import joinedload
from flask import Flask, render_template, request, jsonify, session
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Meme
from flask_login import LoginManager, UserMixin, login_required, current_user
from models import db, Story, Like, Comment
from forms import StoryForm
from models import db, Meme, Like  # Assuming you have a Like model
import uuid
from pydub import AudioSegment
import speech_recognition as sr




app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
MUSIC_FOLDER = "static/music"
OUTPUT_FOLDER = "mixed"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Ensure upload & music directories exist
UPLOAD_FOLDER = "static/uploads"
MUSIC_FOLDER = "static/music"
MIXED_FOLDER = "static/mixed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MUSIC_FOLDER, exist_ok=True)
os.makedirs(MIXED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MIXED_FOLDER"] = MIXED_FOLDER

  # Make sure you have the User model with relationships


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)

app.secret_key = 'supersecretkey'  # Change this in production

# Default user settings
default_settings = {
    "privacy": "public",
    "liked": "",
    "history": "",
    "notifications": "on",
    "theme": "light",
    "saved": "",
    "blocklist": "",
    "twofactor": "disabled",
    "email": "on",
    "language": "english",
    "activity": "visible"
}

CORS(app)  # Allow CORS for frontend communication

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuration
UPLOAD_FOLDER = 'static/uploads'  # Directory to store uploaded memes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
stories = [
    {"id": 1, "title": "Story 1", "likes": 0, "content": "Content of Story 1"},
    # Add more stories here...
]

# Temporary storage for memes (in-memory for demonstration)
memes = []
likes = {}
# Initialize Flask App

app.config['SECRET_KEY'] = 'your-secret-key-here'
# App Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROFILE_PIC_FOLDER'] = 'static/profile_pics'
app.secret_key = "your_secret_key"
# Allowed File Types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Database Initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login Manager Initialization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50), unique=True, nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), default='default.jpg')
    stories = db.relationship('Story', backref='author', lazy=True)

    following = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic"
    )

    # Helper Methods
    def follow(self, user):
        """Follow a user."""
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        """Unfollow a user."""
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """Check if the user is following another user."""
        return self.following.filter(followers.c.followed_id == user.id).count() > 0



# Story Model
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('user.uname'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", backref="story", lazy=True)
    def like_count(self):
        return Like.query.filter_by(story_id=self.id).count()
    def share_count(self):
        return Share.query.filter_by(story_id=self.id).count()
    def comment_count(self):
        return Comment.query.filter_by(story_id=self.id).count()
   # timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Ensure this exists
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #user = db.relationship('User', backref=db.backref('memes', lazy=True))

 

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('user.uname'), nullable=False)
    comment_content = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return f'<Comment {self.username} -> Story {self.story_id}>'

# Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('user.uname'), nullable=False)
    def __repr__(self):
        return f'<Like {self.username} -> Story {self.story_id}>'

class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Ensure this exists
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('memes', lazy=True))
    
class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Share {self.username} -> Story {self.story_id}>'


# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper Function to Check Allowed Files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/handlelogin/', methods=['POST'])
def handle_login():
    username = request.form.get('loginuname')
    password = request.form.get('loginpass')
    user = User.query.filter_by(uname=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/handleSignup/', methods=['POST'])
def handle_signup():
    uname = request.form.get('uname')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password1 = request.form.get('pass1')
    password2 = request.form.get('pass2')

    if password1 != password2:
        flash('Passwords do not match!', 'danger')
        return redirect(url_for('register'))

    if len(password1) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('register'))

    if User.query.filter_by(uname=uname).first() or User.query.filter_by(email=email).first():
        flash("Username or email already exists", "danger")
        return redirect(url_for('register'))

    hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
    new_user = User(uname=uname, fname=fname, lname=lname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash("Account created successfully!", "success")
    return redirect(url_for('login'))
@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found!', 'error')
            return redirect(url_for('reset_password'))

        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('reset_password'))

        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password successfully updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')
@app.route('/games')
@login_required
def game():
    return render_template('games.html')
@app.route('/videos')
@login_required
def videos():
    return render_template('videos.html')
@app.route('/music')
@login_required
def music():
    return render_template('music.html')
@app.route('/rules')
@login_required
def rules():
    return render_template('rules.html')
@app.route('/sing')
@login_required
def sing():
    music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.wav'))]
    
    return render_template('sing.html',music_files=music_files)


@app.route("/upload2", methods=["POST"])
def upload2():
    try:
        file = request.files["file"]
        music_name = request.form["music"]
        volume = int(request.form["volume"])
        username = request.form["username"]

        # Save uploaded voice
        user_filename = f"{username}_{uuid.uuid4().hex}.webm"
        file_path = os.path.join(UPLOAD_FOLDER, user_filename)
        file.save(file_path)

        # Convert to WAV using pydub
        voice = AudioSegment.from_file(file_path)
        voice = voice.set_frame_rate(44100).set_channels(2)

        # Load background music
        music_path = os.path.join(MUSIC_FOLDER, music_name)
        music = AudioSegment.from_file(music_path)
        music = music.set_frame_rate(44100).set_channels(2)

        # Trim or loop music to match voice length
        if len(music) < len(voice):
            loops = len(voice) // len(music) + 1
            music *= loops
        music = music[:len(voice)]

        # Adjust music volume
        music = music - (100 - volume)

        # Mix both
        mixed = music.overlay(voice)

        # Save final audio
        output_filename = f"mixed_{username}_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        mixed.export(output_path, format="mp3")

        # Recognize speech (optional)
        lyrics = recognize_lyrics(file_path)

        return jsonify({
            "filename": output_filename,
            "lyrics": lyrics
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/delete/<filename>", methods=["DELETE"])
def delete(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"{filename} deleted successfully."}), 200
        return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/edit/<filename>", methods=["POST"])
def edit(filename):
    try:
        new_filename = request.form["new_filename"]
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        new_file_path = os.path.join(OUTPUT_FOLDER, new_filename)

        if os.path.exists(file_path):
            os.rename(file_path, new_file_path)
            return jsonify({"message": f"File renamed to {new_filename}."}), 200
        return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def recognize_lyrics(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
    except Exception:
        return "Could not detect lyrics."
    
@app.route('/explore')
@login_required
def explore():
    users = User.query.all()  # Fetch all users
    return render_template('explore.html', users=users)

'''@app.route('/profile1/<int:user_id>')
@login_required
def profile1(user_id):
    user = User.query.get_or_404(user_id)  # Fetch user by ID
    return render_template('profile1.html', user=user)
    '''
@app.route('/profile1/<int:user_id>')
@login_required
def profile1(user_id):
    user = User.query.get_or_404(user_id)  # Fetch user by ID
    memes = Meme.query.filter_by(user_id=user.id).all()  # Fetch memes by user
    stories = Story.query.order_by(Story.id.desc()).all() 

    return render_template('profile1.html', user=user, memes=memes, stories=stories)


@app.route('/profile1/<int:user_id>')
@login_required
def profile_with_id(user_id):
    user = User.query.get_or_404(user_id)  # Fetch user by ID
    return render_template('profile1.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.uname = form.uname.data
        current_user.email = form.email.data
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data
        current_user.bio = form.bio.data

        # Handle profile picture upload
        if form.profile_pic.data:
            filename = save_profile_picture(form.profile_pic.data)
            current_user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile1', user_id=current_user.id))

    return render_template('edit_profile.html', form=form)



class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if user and user != current_user:
        current_user.follow(user)
        return jsonify({"status": "followed"})
    return jsonify({"error": "Cannot follow this user"}), 400

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if user and user != current_user:
        current_user.unfollow(user)
        return jsonify({"status": "unfollowed"})
    return jsonify({"error": "Cannot unfollow this user"}), 400


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user  # Use Flask-Login's current_user
    memes = Meme.query.filter_by(user_id=user.id).all()
    stories = Story.query.order_by(Story.id.desc()).all()
    form = EditProfileForm(obj=user)  # Prefill the form using obj=user

    if form.validate_on_submit():
        user.uname = form.uname.data
        user.email = form.email.data
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.bio = form.bio.data
        user.private_account = form.private_account.data  # This should work now

        # Handle profile picture upload
        if form.profile_pic.data:
            filename = save_profile_picture(form.profile_pic.data)
            user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, user=user, memes=memes, stories=stories)


def save_profile_picture(form_picture):
    # Generate a random hex name for the file to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension

    # Define the path to save the picture
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)

    # Optionally resize the image before saving (uncomment if desired)
    # output_size = (150, 150)
    # img = Image.open(form_picture)
    # img.thumbnail(output_size)
    # img.save(picture_path)

    # Save the uploaded picture
    form_picture.save(picture_path)

    return picture_filename


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/story", methods=["GET", "POST"])
@login_required
def stories():  # Renamed for clarity
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("story")

        if not title or not content:  # Validate empty input
            flash("Title and story content cannot be empty!", "danger")
            return redirect(url_for("stories"))

        new_story = Story(username=current_user.uname, title=title, content=content)
        db.session.add(new_story)
        db.session.commit()

        return redirect(url_for("stories"))  # Avoid duplicate form submission

    stories = Story.query.order_by(Story.id.desc()).all()  # Show newest first

    # Fetch relevant comments & likes
    story_ids = [story.id for story in stories]
    comments = Comment.query.filter(Comment.story_id.in_(story_ids)).all()
    likes = Like.query.filter(Like.story_id.in_(story_ids)).all()
    for story in stories:
        story.comments = Comment.query.filter_by(story_id=story.id).all()

    return render_template("story.html", stories=stories, comments=comments, likes=likes, current_user=current_user)


@app.route('/edit_story/<int:story_id>', methods=['POST'])
def edit_story(story_id):
    story = Story.query.get(story_id)
    if story and story.author_id == current_user.id:
        data = request.get_json()
        story.title = data.get('title', story.title)
        story.content = data.get('content', story.content)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/delete_story/<int:story_id>', methods=['POST'])
def delete_story(story_id):
    story = Story.query.get(story_id)
    if story and story.author_id == current_user.id:
        db.session.delete(story)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/download_story/<int:story_id>')
def download_story(story_id):
    story = Story.query.get(story_id)
    if story:
        file_path = f"static/downloads/story_{story.id}.txt"
        os.makedirs("static/downloads", exist_ok=True)  # Ensure directory exists
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Title: {story.title}\n\n{story.content}")
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route("/like/<int:story_id>", methods=["POST"])
@login_required
def like_story(story_id):
    story = Story.query.get_or_404(story_id)

    # Check if the user has already liked the story
    existing_like = Like.query.filter_by(story_id=story_id, username=current_user.uname).first()

    if existing_like:
        db.session.delete(existing_like)  # Remove like (Unlike)
        liked = False
    else:
        new_like = Like(story_id=story_id, username=current_user.uname)
        db.session.add(new_like)
        liked = True

    db.session.commit()  # **Ensure like is permanently stored in the database**

    # Return the updated like count
    like_count = Like.query.filter_by(story_id=story_id).count()

    return jsonify({"liked": liked, "like_count": like_count})
@app.route("/comment/<int:story_id>", methods=["POST"])
@login_required
def post_comment(story_id):
    data = request.get_json()
    comment_content = data.get("content", "").strip()

    if not comment_content:
        return jsonify({"error": "Comment cannot be empty"}), 400

    story = Story.query.get(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404

    new_comment = Comment(
        story_id=story_id,
        username=current_user.uname,  # Get the logged-in user's username
        content=comment_content
    )

    db.session.add(new_comment)
    db.session.commit()

    # Count total comments after inserting the new one
    comment_count = Comment.query.filter_by(story_id=story_id).count()

    return jsonify({
        "commented": True,
        "username": current_user.uname,  # Send back the username
        "comment_content": comment_content,
        "comment_count": comment_count  # Send updated comment count
    })


@app.route("/comment/<int:story_id>", methods=["POST"])
@login_required
def comment(story_id):
    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "Comment cannot be empty"}), 400

    new_comment = Comment(story_id=story_id, username=current_user.uname, content=content)
    db.session.add(new_comment)
    db.session.commit()

    comment_count = Comment.query.filter_by(story_id=story_id).count()

    return jsonify({"commented": True, "comment_count": comment_count, "username": current_user.uname})

@app.route("/share/<int:story_id>", methods=["POST"])
@login_required
def share_story(story_id):
    story = Story.query.get_or_404(story_id)

    # Check if the user already shared
    existing_share = Share.query.filter_by(story_id=story_id, username=current_user.uname).first()

    if not existing_share:
        new_share = Share(story_id=story_id, username=current_user.uname)
        db.session.add(new_share)
        db.session.commit()

    # Get updated share count
    share_count = Share.query.filter_by(story_id=story_id).count()

    return jsonify({"shared": True, "share_count": share_count})


@app.route("/stories")
@login_required
def view_stories():
    stories = Story.query.order_by(Story.id.desc()).all()
    following = current_user.following.all()  # Get following users
    return render_template("story.html", stories=stories, following=following, current_user=current_user)





# Load available background music files
def get_music_files():
    return [f for f in os.listdir(MUSIC_FOLDER) if f.endswith((".mp3", ".wav"))]


@app.route("/upload1", methods=["POST"])
def upload1():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    background_music = request.form.get("music")
    volume = int(request.form.get("volume", 50))
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Mix with background music
    mixed_filename = "mixed_" + filename
    mixed_filepath = os.path.join(app.config["MIXED_FOLDER"], mixed_filename)

    try:
        vocal_audio = AudioSegment.from_file(filepath)
        bg_music = AudioSegment.from_file(os.path.join(MUSIC_FOLDER, background_music))

        bg_music = bg_music - (100 - volume)  # Adjust volume
        combined = vocal_audio.overlay(bg_music)

        combined.export(mixed_filepath, format="mp3")
        
        # Get lyrics using Speech-to-Text
        recognizer = sr.Recognizer()
        with sr.AudioFile(filepath) as source:
            audio_data = recognizer.record(source)
            lyrics = recognizer.recognize_google(audio_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "filename": mixed_filename,
        "lyrics": lyrics
    })

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["MIXED_FOLDER"], filename)


@app.route('/upload_meme')
def upload_meme():
    """Render the upload page."""
    return render_template('upload_meme.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/memes')
def memes():
    
    memes = Meme.query.order_by(Meme.id.desc()).all()
    print(memes)  # Debugging: See if memes are retrieved
    return render_template('memes.html', memes=memes)
# Edit Meme Caption
@app.route('/edit_meme/<int:meme_id>', methods=['POST'])
def edit_meme(meme_id):
    meme = Meme.query.get(meme_id)
    if meme and meme.user_id == current_user.id:
        data = request.get_json()
        meme.caption = data['caption']
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

# Delete Meme
@app.route('/delete_meme/<int:meme_id>', methods=['POST'])
def delete_meme(meme_id):
    meme = Meme.query.get(meme_id)
    if meme and meme.user_id == current_user.id:
        db.session.delete(meme)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

# Download Meme
@app.route('/download_meme/<int:meme_id>')
def download_meme(meme_id):
    meme = Meme.query.get(meme_id)
    if meme:
        file_path = os.path.join('static/uploads', meme.file_path)
        return send_from_directory(directory='static/uploads', filename=meme.file_path, as_attachment=True)
    return "File not found", 404
@app.route('/toggle_follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    user_to_follow = User.query.get(user_id)
    if not user_to_follow:
        return jsonify({"status": "User not found"}), 404

    if current_user.is_following(user_to_follow):
        current_user.unfollow(user_to_follow)
        db.session.commit()
        return jsonify({"status": "Follow"})
    else:
        current_user.follow(user_to_follow)
        db.session.commit()
        return jsonify({"status": "Following"})

@app.route('/like/<int:meme_id>', methods=['POST'])
@login_required
def like_meme(meme_id):
    meme = Meme.query.get_or_404(meme_id)
    existing_like = Like.query.filter_by(meme_id=meme.id, username=current_user.uname).first()

    if existing_like:  # ✅ Already liked
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"liked": False, "already_liked": True})  

    new_like = Like(meme_id=meme.id, username=current_user.uname)
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"liked": True, "already_liked": False})


@app.route('/add_comment/<int:meme_id>', methods=['POST'])
def add_comment(meme_id):  # Renamed function
    data = request.get_json()

    username = data.get("username")
    content = data.get("content")

    if not content:
        return jsonify({"success": False, "message": "Comment cannot be empty!"})

    meme = Meme.query.get(meme_id)
    if not meme:
        return jsonify({"success": False, "message": "Meme not found!"})

    new_comment = Comment(username=username, content=content, meme_id=meme_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"success": True, "message": "Comment posted successfully!"})

@app.route('/share/<int:meme_id>', methods=['POST'])
@login_required  # Remove if causing issues
def share_meme(meme_id):
    meme = Meme.query.get(meme_id)  # Get the meme
    if not meme:
        return jsonify({"error": "Meme not found"}), 404  # Return an error if meme doesn't exist

    meme.shares += 1  # Increase share count
    db.session.commit()  # Save to database

    return jsonify({"shares": meme.shares})  # Return updated shares

@app.route('/get_comments/<int:meme_id>', methods=['GET'])
def get_comments(meme_id):
    comments = Comment.query.filter_by(meme_id=meme_id).order_by(Comment.timestamp.desc()).all()
    return jsonify({'comments': [{'id': c.id, 'text': c.text, 'timestamp': c.timestamp} for c in comments]})


@app.route('/get_following_list')
@login_required
def get_following_list():
    following_users = [
        {"id": user.id, "uname": user.uname, "profile_pic": user.profile_pic or "default.png"}
        for user in current_user.following.all()
    ]
    return jsonify({"following": following_users})

# ✅ Ensure the /upload route allows POST requests
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for("memes"))

    file = request.files['file']
    caption = request.form.get('caption', '')

    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for("memes"))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        new_meme = Meme(user_id=current_user.id, file_path=file_path, caption=caption)
        db.session.add(new_meme)
        db.session.commit()

        flash("Meme uploaded successfully!", "success")

    return redirect(url_for("memes"))

# ✅ Ensure /index is accessible
@app.route("/index", methods=["GET"])
@login_required
def index():
    memes = Meme.query.all()
    return render_template("index.html", memes=memes)

    
'''@app.route('/story1')
@login_required
def story1():
    return render_template('story1.html')'''

# Route to serve frontend (assuming index.html is in a 'static' folder)
@app.route('/story1')
@login_required
def story1():
    return render_template('story1.html')

# Route to upload an audio file
@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    return jsonify({'error': 'Invalid file format'})

@app.route('/recordings')
def list_recordings():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({'recordings': files})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to delete a file
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"}), 200
    return jsonify({"error": "File not found"}), 404


@app.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html')

@app.route('/get-settings', methods=['GET'])
def get_settings():
    settings = session.get('settings', default_settings)
    return jsonify(settings)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    data = request.json
    session['settings'] = data  # Save in session (use a database for persistent storage)
    return jsonify({"message": "Settings saved successfully!"})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    settings = session.get('settings', default_settings)
    settings['history'] = ""  # Clear search history
    session['settings'] = settings
    return jsonify({"message": "Search history cleared!"})

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
