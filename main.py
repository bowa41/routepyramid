from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean


'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routepyramid.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Sends(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    # def to_dict(self):
    #     # Method 1.
    #     # dictionary = {}
    #     # # Loop through each column in the data record
    #     # for column in self.__table__.columns:
    #     #     # Create a new dictionary entry;
    #     #     # where the key is the name of the column
    #     #     # and the value is the value of the column
    #     #     dictionary[column.name] = getattr(self, column.name)
    #     # return dictionary
    #
    #     # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    #     return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

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
    return jsonify(cafe=random_cafe.to_dict())

# @app.route("/search/", methods=['GET', 'POST'])
# def get_local_cafes():
#     # select records from the database based on location.
#     location = request.form['location_query']
#     local_cafes = db.session.query(Cafe).filter_by(location=location)
#     if local_cafes:
#         return jsonify(cafes=[cafe.to_dict() for cafe in local_cafes])
#     return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/all")
def get_all_cafes():
    # select all records from the database.
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


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
