from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.core import BooleanField, FloatField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired
from wtforms.widgets.html5 import NumberInput

class RegisterForm(FlaskForm):
    """Form for registering."""

    displayname = StringField('Display Name', validators=[DataRequired(Length(min=6))])
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(Length(min=6)), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    """Form for logging in."""
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])


class NewGameForm(FlaskForm):
    """Form for creating a new game"""
    fractional_shares = BooleanField('Allow Fractional Shares')
    max_players = IntegerField('Maximum Players', 
                                        widget=NumberInput(min = 1, max = 15, step = 1), 
                                        validators=[InputRequired()],
                                        default=4)
                                        
    days = IntegerField('Days', 
                                        widget=NumberInput(min = 0, max = 90, step = 1), 
                                        validators=[InputRequired()],
                                        default=0)
                                        
    hours = IntegerField('Hours', 
                                        widget=NumberInput(min = 0, max = 24, step = 1), 
                                        validators=[InputRequired()],
                                        default=0)
    minutes = IntegerField('Minutes', 
                                        widget=NumberInput(min = 0, max = 60, step = 1), 
                                        validators=[InputRequired()],
                                        default=15)

    starting_balance = FloatField('Starting Balance', validators=[InputRequired()],
                                    default = 1000)