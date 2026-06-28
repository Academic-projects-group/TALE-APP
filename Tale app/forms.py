from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class EditProfileForm(FlaskForm):
    uname = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    profile_pic = FileField('Profile Picture', validators=[Optional()])  # Optional profile pic
    private_account = BooleanField('Private Account')

    # Additional fields (optional)
    current_password = PasswordField('Current Password', validators=[Optional(), Length(min=6, max=100)])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm New Password', validators=[Optional(), Length(min=6, max=100)])


class StoryForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Your Story", validators=[DataRequired()])
    submit = SubmitField("Upload Story")
