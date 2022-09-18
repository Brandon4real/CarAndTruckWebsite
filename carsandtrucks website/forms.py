from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, MultipleFileField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class UploadCarForm(FlaskForm):
    type_of_car = StringField("Used or Occasion Belgique", validators=[DataRequired()])
    price_of_car = StringField("Price of car", validators=[DataRequired()])
    car_description = StringField("Car Type e.g Kompressor c220", validators=[DataRequired()])
    propulsion = StringField("Petrol or Diesel", validators=[DataRequired()])
    make_of_car = StringField("Car Model Year", validators=[DataRequired()])
    gear_box = StringField("Gear Box Type e.g Automatic", validators=[DataRequired()])
    kilometers = StringField("Kilometers Covered *OPTIONAL")
    full_option = StringField("Full Option? Yes or No", validators=[DataRequired()])
    tel_number = StringField("Telephone number", validators=[DataRequired()])
    files = MultipleFileField('File(s) Upload', validators=[DataRequired()])
    submit = SubmitField("Upload Now",)


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    tel_number = StringField("Telephone Number", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In!")


class UploadTruckForm(FlaskForm):
    type_of_truck = StringField("Used or Occasion Belgique", validators=[DataRequired()])
    price_of_Truck = StringField("Price of Truck", validators=[DataRequired()])
    truck_description = StringField("Truck Type e.g Mercedes 3340,MAN Diesel", validators=[DataRequired()])
    propulsion = StringField("Diesel or Hybrid?", validators=[DataRequired()])
    number_of_tyres = StringField("How many tyres?", validators=[DataRequired()])
    gear_box = StringField("Gear Box Type e.g Automatic", validators=[DataRequired()])
    tel_number = StringField("Telephone Number", validators=[DataRequired()])
    files = MultipleFileField('File(s) Upload', validators=[DataRequired()])
    submit = SubmitField("Upload Now")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")