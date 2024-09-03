import werkzeug
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_from_directory
from sqlalchemy import Integer, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField
from flask_font_awesome import FontAwesome
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired
from datetime import datetime, date
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from sshtunnel import SSHTunnelForwarder
import pymysql

user = os.environ.get('USERID')
password = os.environ.get('PASSWORD')
# host = os.environ.get('HOST')
port = '5432'
database = 'route_pyramid'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')


# Create SSH Tunnel
forwarding_server = SSHTunnelForwarder(
    ('ec2-3-19-123-56.us-east-2.compute.amazonaws.com', 22),  # Remote server IP and SSH port
    ssh_username='ec2-user',
    ssh_pkey='/myec2key.pem',
    remote_bind_address=('routepyramid.cbcgckmumb6w.us-east-2.rds.amazonaws.com', 5432)
    )

forwarding_server.start()
print("server connected")

# connect to PostgreSQL
local_port = forwarding_server.local_bind_port
connection_str = f'postgresql://{user}:{password}@localhost:{local_port}/{database}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_str

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database

db = SQLAlchemy(model_class=Base)
db.init_app(app)
font_awesome = FontAwesome(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Sends TABLE Configuration
class Sends(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)
    year:  Mapped[str] = mapped_column(String(4), nullable=False)
    route_name: Mapped[str] = mapped_column(String(250), nullable=False)
    ascent_type: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    angle: Mapped[str] = mapped_column(String(20), nullable=False)
    style: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self):
        # Use Dictionary Comprehension to create json
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Grade(db.Model):
    grade_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade_style: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)

class Angle(db.Model):
    angle_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    angle: Mapped[str] = mapped_column(String(20), nullable=False)

class Ascent_type(db.Model):
    ascent_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ascent_type: Mapped[str] = mapped_column(String(20), nullable=False)

class Style(db.Model):
    style_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    style: Mapped[str] = mapped_column(String(20), nullable=False)

#create user table
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

with app.app_context():
    db.create_all()

# create date dropdown for Form
    date_list = [(year.year, year.year) for year in (db.session.query(Sends).order_by("year").distinct())]
    date_list = list(dict.fromkeys(date_list))

class FilterForm(FlaskForm):
    climbing_style = SelectField("Climbing Style",
                                 choices=[("route", "Route"), ("boulder", "Boulder")])

    grade = SelectField("Grade", choices=[])

    pyramid_levels = SelectField("Levels",
                                 choices=[("1","1"), ("2","2"),("3","3"),("4","4"),("5","5"),
                                          ("6","6"), ("7","7"), ("8","8"), ("9","9"), ("10","10")],
                                 default="8")

    style_list = ["Compression","Pockets","Crimps","Jugs","Incuts","Jam","Pinch","Slopers","Tufa"]
    style = SelectMultipleField("Choose your option",
                                choices=[("Compression","Compression"), ("Pockets","Pockets"),
                                         ("Crimps","Crimps"), ("Jugs","Jugs"),
                                         ("Incuts","Incuts"), ("Jam","Jam"), ("Pinch","Pinch"),
                                         ("Slopers","Slopers"), ("Tufa","Tufa")],
                                default=style_list)

    angle_list = ["Slab","Vertical","Overhang","Roof"]
    angle = SelectMultipleField("Choose your option",
                                choices=[("Slab","Slab"), ("Vertical","Vertical"),
                                        ("Overhang","Overhang"), ("Roof","Roof")],
                                default=angle_list)

    year = SelectMultipleField("Choose your option", choices=(date_list), default=[str(datetime.now().year)])

class AddForm(FlaskForm):
    # add_form = SubmitField('Add')
    climb_name = StringField("Climb Name", render_kw={"placeholder": "Climb Name"})

    send_date = DateField(
        'Date',
        default=date.today(),
        validators=[DataRequired()]
    )

    grade = SelectField("Grade", choices=[ ("1", "v1"), ("2", "v2"), ("3", "v3"),("4", "v4"),
        ("5", "v5"), ("6", "v6"),  ("7", "v7"), ("8", "v8"), ("9", "v9"), ("10", "v10"), ("11", "v11"), ("12", "v12"),
        ("13", "v13"), ("14", "v14"), ("15", "v15"), ("16", "v16"), ("17", "v17"),("18", "5.10a"), ("19", "5.10b"),
        ("20", "5.10c"), ("21", "5.10d"), ("22", "5.11a"), ("23", "5.11b"), ("24", "5.11c"),("25", "5.11d"), ("26", "5.12a"),
        ("27", "5.12b"), ("28", "5.12c"), ("29", "5.12d"),  ("30", "5.13a"),("31", "5.13b"), ("32", "5.13c"),
        ("33", "5.13d"), ("34", "5.14a"), ("35", "5.14b"),  ("36", "5.14c"), ("37", "5.14d"), ("38", "5.15a"),
        ("39", "5.15b"), ("40", "5.15c"), ("41", "5.15d")], render_kw={"id": "submit_grade"})


    ascent = SelectField("Choose your option",
                        choices=[("Onsight", "Onsight"), ("Redpoint", "Redpoint")], render_kw={"id": "submit_ascent"})

    style = SelectField("Choose your option",
                                choices=[("Compression","Compression"), ("Pockets","Pockets"),
                                         ("Crimps","Crimps"), ("Jugs","Jugs"),
                                         ("Incuts","Incuts"), ("Jam","Jam"), ("Pinch","Pinch"),
                                         ("Slopers","Slopers"), ("Tufa","Tufa")], render_kw={"id": "submit_style"})

    angle = SelectField("Choose your option",
                                choices=[("Slab","Slab"), ("Vertical","Vertical"),
                                        ("Overhang","Overhang"), ("Roof","Roof")], render_kw={"id": "submit_angle"})

    # send_date = SelectField("Choose your option", choices=(date_list), default=[str(datetime.now().year)])

def write_data(add_form):
    # Add new send to db
    new_send = Sends(user_id=current_user.id,
                     date=add_form.send_date.data.strftime("%Y-%m-%d"),
                     year=str(add_form.send_date.data)[:4],
                     route_name=add_form.climb_name.data,
                     ascent_type=add_form.ascent.data,
                     grade=db.session.query(Grade).filter(Grade.grade_id == add_form.grade.data).first().grade,
                     angle=add_form.angle.data,
                     style=add_form.style.data)
    db.session.add(new_send)
    db.session.commit()
def read_data(form):
    grade = Grade.query.filter_by(grade_id=form.grade.data).first()
    grade_list = [grade.grade for grade in
                  Grade.query.filter_by(grade_style=form.climbing_style.data)
                  .where(Grade.grade_id <= grade.grade_id).all()]
    slice_grade_list = grade_list[-int(form.pyramid_levels.data):]

    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Sends).where(Sends.grade.in_(slice_grade_list))
                                .where(Sends.user_id == current_user.id)
                                .where(Sends.style.in_(form.style.data))
                                .where(Sends.angle.in_(form.angle.data))
                                .where(Sends.year.in_(form.year.data)).order_by("date"))

    # Use .scalars() to get the elements rather than entire rows from the database
    selected_sends = result.scalars().all()

    outer_list = []

    for grade in grade_list[::-1]:
        inner_list = []
        for send in selected_sends:
            if send.grade == grade:
                inner_list.append({"name": send.route_name, "date": send.date, "ascent": send.ascent_type})
        if len(inner_list) > 0:
            outer_list.append({"grade": grade, "climbs": inner_list})
    return outer_list

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



@app.route("/", methods=["GET", "POST"])
def index():
    print("test2")
    if current_user.is_authenticated:
        return redirect(url_for("home"))


    return render_template("index.html")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = FilterForm()
    add_form = AddForm()


    # set filter for first time load
    if not form.climbing_style.data:
        form.climbing_style.data = "route"
        db_results = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                      .filter(Grade.grade_style == 'route', Sends.user_id == current_user.id).first())
        if db_results:
            highest_route = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                             .filter(Grade.grade_style == 'route', Sends.user_id == current_user.id)
                             .order_by(Grade.grade.desc()).first())
            send, grade = highest_route
            form.grade.data = str(grade.grade_id)
            print(grade.grade_id)

        else:
            form.grade.data = "30"

    # get all grades for the selected climbing style
    form.grade.choices = [(grade.grade_id, grade.grade) for grade in
                          Grade.query.filter_by(grade_style=form.climbing_style.data).all()]


    #find highest bouldering grade
    if (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                      .filter(Grade.grade_style == 'boulder' and Sends.user_id == current_user.id).first()):
        highest_boulder = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                             .filter(Grade.grade_style == 'boulder' and Sends.user_id == current_user.id).order_by(Grade.grade.desc()).first())
        send, grade = highest_boulder
        highest_boulder_grade = grade.grade
    else:
        highest_boulder_grade = "v0"

    if add_form.validate_on_submit():
        write_data(add_form)
        return redirect(url_for('home'))

    # On submit, search for the selected grade and filter
    if form.validate_on_submit:
        output = read_data(form)

        return render_template('home.html', layers=output, form=form, add_form=add_form, current_user=current_user.name)

    return render_template("home.html", form=form, add_form=add_form, highest_boulder=highest_boulder_grade,current_user=current_user.name)

@app.route("/grades/<style>")
@login_required
def climbing_grades(style):
    grades = Grade.query.filter_by(grade_style=style).all()
    grade_list = []

    for grade in grades:
        gradeobj = {'id': grade.grade_id, 'grade': grade.grade}
        grade_list.append(gradeobj)
    return jsonify({"grades" : grade_list})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        # Hashing and salting the password entered by the user
        new_user = User(name = request.form.get("name"),
                     email = email,
                    password = generate_password_hash(password,
                                                      method='pbkdf2:sha256',
                                                      salt_length=8)
                    )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)

        # Can redirect() and get name from the current_user
        return redirect(url_for("home"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Check stored password hash against entered password hashed.
        if not user:
            flash("That email does not exist, please try again.")
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=False)
            return redirect(url_for("home"))


    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
