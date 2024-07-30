from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import SelectField


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routepyramid.db'
app.config['SECRET_KEY'] = 'secret'

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database

db = SQLAlchemy(model_class=Base)
db.init_app(app)

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
    form.grade.choices = [(grade.grade_id, grade.grade) for grade in Grade.query.filter_by(grade_style="Route").all()]
    # select all records from the database for specific user.
    all_sends = db.session.execute(db.select(Sends).order_by("date")).scalars().all()
    # return jsonify(sends=[send.to_dict() for send in all_sends])
    return render_template("index.html", sends=all_sends, form=form)

# @app.route("/random")
# def get_random_cafe():
#     # select single random record from the database.
#     random_cafe = db.session.execute(db.select(Cafe).order_by(db.sql.func.random()).limit(1)).scalar()

    #Simple return solution

    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })

    #Fancy return solution

    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })

    # convert to dictionary using a function and let flask automatically convert to json
    # return jsonify(cafe=random_cafe.to_dict())

# @app.route("/search/", methods=['GET', 'POST'])
# def get_local_cafes():
#     # select records from the database based on location.
#     location = request.form['location_query']
#     local_cafes = db.session.query(Cafe).filter_by(location=location)
#     if local_cafes:
#         return jsonify(cafes=[cafe.to_dict() for cafe in local_cafes])
#     return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# @app.route("/all")
# def get_all_cafes():
#     # select all records from the database.
#     all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
#     return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


# @app.route("/add", methods=['GET', 'POST'])
# def add_cafe():
#     # add new record to db.
#     with app.app_context():
#         new_cafe = Cafe(name=request.form.get("name"),
#                         map_url=request.form.get("map_url"),
#                         img_url=request.form.get("img_url"),
#                         location=request.form.get("loc"),
#                         seats=request.form.get("seats"),
#                         has_toilet=bool(request.form.get("toilet")),
#                         has_wifi=bool(request.form.get("wifi")),
#                         has_sockets=bool(request.form.get("sockets")),
#                         can_take_calls=bool(request.form.get("calls")),
#                         coffee_price=request.form.get("coffee_price"))
#         db.session.add(new_cafe)
#         db.session.commit()
#     return jsonify(response={"success": "Successfully added the new cafe."})

if __name__ == '__main__':
    app.run(debug=True)
