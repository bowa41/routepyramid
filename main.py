import werkzeug
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_from_directory
from sqlalchemy import Integer, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField
from flask_fontawesome import FontAwesome
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired
from datetime import datetime, date
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from sshtunnel import SSHTunnelForwarder
import pymysql

user = 'postgres'
password = 'jadynrocks'
# host = os.environ.get('HOST')
port = '5432'
database = 'route_pyramid'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', 'dev-secret-key')

print(user)
host = 'localhost'

connection_str = f'postgresql://{user}:{password}@localhost:{port}/{database}'
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

ADMIN_EMAIL = 'bowa41@att.net'
GUEST_EMAIL = 'guest@routepyramid.com'

with app.app_context():
    db.create_all()

    # Create guest user if it doesn't exist
    guest = db.session.execute(db.select(User).where(User.email == GUEST_EMAIL)).scalar()
    if not guest:
        guest = User(name='Guest', email=GUEST_EMAIL,
                     password=generate_password_hash('', method='pbkdf2:sha256', salt_length=8))
        db.session.add(guest)
        db.session.commit()

# create date dropdown for Form
    date_list = [(year.year, year.year) for year in (db.session.query(Sends).order_by("year").distinct())]
    date_list = list(dict.fromkeys(date_list))

class FilterForm(FlaskForm):
    climbing_style = SelectField("Climbing Style",
                                 choices=[("route", "Route"), ("boulder", "Boulder")])

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
def read_data(form, user_id, grade_id):
    grade = Grade.query.filter_by(grade_id=grade_id).first()
    grade_list = [grade.grade for grade in
                  Grade.query.filter_by(grade_style=form.climbing_style.data)
                  .where(Grade.grade_id <= grade.grade_id).all()]
    slice_grade_list = grade_list[-int(form.pyramid_levels.data):]

    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Sends).where(Sends.grade.in_(slice_grade_list))
                                .where(Sends.user_id == user_id)
                                .where(Sends.style.in_(form.style.data))
                                .where(Sends.angle.in_(form.angle.data))
                                .where(Sends.year.in_(form.year.data)).order_by("date"))

    # Use .scalars() to get the elements rather than entire rows from the database
    selected_sends = result.scalars().all()

    outer_list = []

    for grade in grade_list[::-1]:
        inner_list = []
        seen_routes = set()
        for send in selected_sends:
            if send.grade == grade and send.route_name not in seen_routes:
                seen_routes.add(send.route_name)
                inner_list.append({"name": send.route_name, "date": send.date, "ascent": send.ascent_type})
        if len(inner_list) > 0:
            outer_list.append({"grade": grade, "climbs": inner_list})
    return outer_list

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



@app.route("/guest-login")
def guest_login():
    guest = db.session.execute(db.select(User).where(User.email == GUEST_EMAIL)).scalar()
    login_user(guest, remember=False)
    return redirect(url_for("home"))

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))


    return render_template("index.html")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = FilterForm()
    add_form = AddForm()

    is_admin = current_user.email == ADMIN_EMAIL
    is_guest = current_user.email == GUEST_EMAIL
    all_users = User.query.filter(User.email != GUEST_EMAIL).all() if (is_admin or is_guest) else []

    # Determine which user's data to show
    view_user_id = current_user.id
    view_user_name = current_user.name
    if is_admin or is_guest:
        selected_id = request.form.get('view_user_id') or request.args.get('view_user_id')
        if selected_id:
            view_user_id = int(selected_id)
            view_user = db.session.get(User, view_user_id)
            if view_user:
                view_user_name = view_user.name
        elif is_guest and all_users:
            view_user_id = all_users[0].id
            view_user_name = all_users[0].name

    # set filter for first time load
    if not form.climbing_style.data:
        form.climbing_style.data = "route"

    year_filter = form.year.data or [str(datetime.now().year)]
    grade_id = request.form.get('grade')
    if not grade_id:
        highest_route = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                         .filter(Grade.grade_style == form.climbing_style.data,
                                 Sends.user_id == view_user_id,
                                 Sends.year.in_(year_filter))
                         .order_by(Grade.grade_id.desc()).first())
        grade_id = str(highest_route[1].grade_id) if highest_route else "30"


    #find highest bouldering grade
    if (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                      .filter(Grade.grade_style == 'boulder' and Sends.user_id == view_user_id).first()):
        highest_boulder = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
                             .filter(Grade.grade_style == 'boulder' and Sends.user_id == view_user_id).order_by(Grade.grade.desc()).first())
        send, grade = highest_boulder
        highest_boulder_grade = grade.grade
    else:
        highest_boulder_grade = "v0"

    if add_form.validate_on_submit():
        write_data(add_form)
        return redirect(url_for('home'))

    # On submit, search for the selected grade and filter
    if form.validate_on_submit:
        output = read_data(form, view_user_id, grade_id)

        return render_template('home.html', layers=output, form=form, add_form=add_form,
                               current_user=view_user_name, is_admin=is_admin, is_guest=is_guest,
                               all_users=all_users, view_user_id=view_user_id, grade_id=grade_id,
                               now=datetime.now())

    return render_template("home.html", form=form, add_form=add_form, highest_boulder=highest_boulder_grade,
                           current_user=view_user_name, is_admin=is_admin, is_guest=is_guest,
                           all_users=all_users, view_user_id=view_user_id, grade_id=grade_id,
                           now=datetime.now())

@app.route("/api/highest-grade")
@login_required
def api_highest_grade():
    climbing_style = request.args.get('climbing_style', 'route')
    years = request.args.getlist('year') or [str(datetime.now().year)]

    view_user_id = current_user.id
    if current_user.email in (ADMIN_EMAIL, GUEST_EMAIL):
        selected_id = request.args.get('view_user_id')
        if selected_id:
            view_user_id = int(selected_id)
        elif current_user.email == GUEST_EMAIL:
            first_user = User.query.filter(User.email != GUEST_EMAIL).first()
            if first_user:
                view_user_id = first_user.id

    highest = (db.session.query(Sends, Grade).join(Grade, Sends.grade == Grade.grade)
               .filter(Grade.grade_style == climbing_style, Sends.user_id == view_user_id,
                       Sends.year.in_(years))
               .order_by(Grade.grade_id.desc()).first())

    if highest:
        send, grade = highest
        return jsonify({"grade_id": grade.grade_id})
    return jsonify({"grade_id": None})

@app.route("/api/pyramid")
@login_required
def api_pyramid():
    climbing_style = request.args.get('climbing_style', 'route')
    grade_id = request.args.get('grade', '30')
    pyramid_levels = request.args.get('pyramid_levels', '8')
    styles = request.args.getlist('style')
    angles = request.args.getlist('angle')
    years = request.args.getlist('year')

    view_user_id = current_user.id
    if current_user.email in (ADMIN_EMAIL, GUEST_EMAIL):
        selected_id = request.args.get('view_user_id')
        if selected_id:
            view_user_id = int(selected_id)
        elif current_user.email == GUEST_EMAIL:
            first_user = User.query.filter(User.email != GUEST_EMAIL).first()
            if first_user:
                view_user_id = first_user.id

    grade = Grade.query.filter_by(grade_id=grade_id).first()
    if not grade:
        return jsonify([])

    grade_list = [g.grade for g in Grade.query.filter_by(grade_style=climbing_style)
                  .where(Grade.grade_id <= grade.grade_id).all()]
    slice_grade_list = grade_list[-int(pyramid_levels):]

    if not styles:
        styles = ["Compression","Pockets","Crimps","Jugs","Incuts","Jam","Pinch","Slopers","Tufa"]
    if not angles:
        angles = ["Slab","Vertical","Overhang","Roof"]
    if not years:
        years = [str(datetime.now().year)]

    result = db.session.execute(
        db.select(Sends).where(Sends.grade.in_(slice_grade_list))
        .where(Sends.user_id == view_user_id)
        .where(Sends.style.in_(styles))
        .where(Sends.angle.in_(angles))
        .where(Sends.year.in_(years))
        .order_by("date")
    )
    selected_sends = result.scalars().all()

    outer_list = []
    for grade in grade_list[::-1]:
        inner_list = []
        seen_routes = set()
        for send in selected_sends:
            if send.grade == grade and send.route_name not in seen_routes:
                seen_routes.add(send.route_name)
                inner_list.append({"name": send.route_name, "date": send.date, "ascent": send.ascent_type})
        if inner_list:
            outer_list.append({"grade": grade, "climbs": inner_list})

    return jsonify(outer_list)

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)

