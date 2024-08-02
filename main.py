from flask import Flask, jsonify, render_template, request
from sqlalchemy import Integer, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_font_awesome import FontAwesome

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routepyramid.db'
app.config['SECRET_KEY'] = 'secret'

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database

db = SQLAlchemy(model_class=Base)
db.init_app(app)
font_awesome = FontAwesome(app)


#Create Flask Filters
class FilterForm(FlaskForm):
    climbing_style = SelectField("Climbing Style", choices=[("route", "Route"), ("boulder", "Boulder")])
    grade = SelectField("Grade", choices=[])

# Sends TABLE Configuration
class Sends(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)
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


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    form = FilterForm()
    # set filter for first time load
    if not form.climbing_style.data:
        form.climbing_style.data = "route"

    # get all grades for the selected climbing style
    form.grade.choices = [(grade.grade_id, grade.grade) for grade in
                          Grade.query.filter_by(grade_style=form.climbing_style.data).all()]

    # select all records from the database for specific user.
    all_sends = db.session.execute(db.select(Sends).order_by("date")).scalars().all()

    # On submit, search for the selected grade and filter
    if request.method == 'POST':
        grade = Grade.query.filter_by(grade_id=form.grade.data).first()
        grade_list = [grade.grade for grade in
                          Grade.query.filter_by(grade_style=form.climbing_style.data)
                          .where(Grade.grade_id <= grade.grade_id).all()]

        # Construct a query to select from the database. Returns the rows in the database
        result = db.session.execute(db.select(Sends).where(Sends.grade.in_(grade_list)).order_by("date"))

        # Use .scalars() to get the elements rather than entire rows from the database
        selected_sends = result.scalars().all()

        outer_list = []

        for grade in grade_list[::-1]:
            inner_list = []
            for send in selected_sends:
                if send.grade == grade:
                    print(send.route_name)
                    inner_list.append({"name":send.route_name, "date":send.date, "ascent":send.ascent_type})
            if len(inner_list) > 0:
                outer_list.append({"grade":grade, "climbs": inner_list})

        return render_template('index.html', sends=selected_sends, layers=outer_list, form=form)
        # return '<h1>Style: {}, Grade: {}</h1>'.format(form.climbing_style.data, grade.grade)

    return render_template("index.html", sends=all_sends, form=form)

@app.route("/grades/<style>")
def climbing_grades(style):
    grades = Grade.query.filter_by(grade_style=style).all()
    grade_list = []

    for grade in grades:
        gradeobj = {}
        gradeobj['id'] = grade.grade_id
        gradeobj['grade'] = grade.grade
        grade_list.append(gradeobj)
    return jsonify({"grades" : grade_list})


if __name__ == '__main__':
    app.run(debug=True)
