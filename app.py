from flask import Flask, json, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
import string

import pymongo

app = Flask (__name__)
CORS(app)

client = MongoClient( "mongodb://127.0.0.1:27017" )
db = client.VehicleDB
vehicles = db.vehicles

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

app.json_encoder = MyEncoder

# SHOW ALL VEHICLES [GET]
@app.route("/api/v1.0/vehicles", methods=["GET"])
def show_all_vehicles():

    page_num, page_size = 1, 10
    if request.args.get("pn"):
        page_num = int(request.args.get('pn'))
    if request.args.get("ps"):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))

    data_to_return = []
    #Queries the database to sort the database from descending order
    for vehicle in vehicles.find().sort('_id', pymongo.DESCENDING).skip(page_start).limit(page_size):
        vehicle["_id"] = str(vehicle["_id"])
        data_to_return.append(vehicle)

    return make_response( jsonify( data_to_return ), 200)

# SHOW ONE VEHICLE [GET]
@app.route("/api/v1.0/vehicles/<string:id>", methods=["GET"])
def show_one_vehicle(id):
    #Validation for length of vehicle Id
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error!" : "Invalid Vehicle ID" } ), 404 )

    vehicle = vehicles.find_one( { "_id" : ObjectId(id) } )
    if vehicle is not None:
        vehicle["_id"] = str(vehicle["_id"])
        return make_response( jsonify ( vehicle ), 200)
    else:
        make_response( jsonify( {"Error!" : "Invalid Vehicle ID" } ), 404)
    
# ADD A VEHICLE [POST]
@app.route("/api/v1.0/vehicles", methods=["POST"])
def add_vehicle():
    #Search for all Vehicle fields from database
    if "Make" in request.form and "Model" in request.form and "Year" in request.form and "Engine_Fuel_Type" in request.form and "Horsepower" in request.form \
        and "Transmission" in request.form and "Driven_Wheels" in request.form and "Number_of_Doors" in request.form and "Market_Category" in request.form \
        and "Vehicle_Style" in request.form and "Price" in request.form and "image_link" in request.form:
        new_vehicle = {
            "_id" : ObjectId(),
            "Make" : request.form["Make"],
            "Model" : request.form["Model"],
            "Year" : request.form["Year"],
            "Engine_Fuel_Type" : request.form["Engine_Fuel_Type"],
            "Horsepower" : request.form["Horsepower"],
            "Transmission" : request.form["Transmission"],
            "Driven_Wheels" : request.form["Driven_Wheels"],
            "Number_of_Doors" : request.form["Number_of_Doors"],
            "Market_Category" : request.form["Market_Category"],
            "Vehicle_Style" : request.form["Vehicle_Style"],
            "Price" : request.form["Price"],
            "image_link" : request.form["image_link"]
        }
        new_vehicle_id = vehicles.insert_one(new_vehicle)
        new_vehicle_link = "http://localhost:5000/api/v1.0/vehicles/" + str(new_vehicle_id.inserted_id)
        return make_response( jsonify( { "url" : new_vehicle_link } , 201) )
    else:
        return make_response( jsonify( { "Error" : "Incomplete Form data! Please try again."} ), 404)

# EDIT A VEHICLE [PUT]
@app.route("/api/v1.0/vehicles/<string:id>", methods=["PUT"])
def edit_vehicle(id):
    #Search for all Vehicle fields from database
    if "Make" in request.form and "Model" in request.form and "Year" in request.form and "Engine_Fuel_Type" in request.form and "Horsepower" in request.form \
    and "Transmission" in request.form and "Driven_Wheels" in request.form and "Number_of_Doors" in request.form and "Market_Category" in request.form \
    and "Vehicle_Style" in request.form and "Price" in request.form:
        new_vehicle = vehicles.update_one({"_id": ObjectId(id)}, {"$set": 
            {"Make": request.form["Make"], 
            "Model" : request.form["Model"],
            "Year" : request.form["Year"],
            "Engine_Fuel_Type" : request.form["Engine_Fuel_Type"],
            "Horsepower" : request.form["Horsepower"],
            "Transmission" : request.form["Transmission"],
            "Driven_Wheels" : request.form["Driven_Wheels"],
            "Number_of_Doors" : request.form["Number_of_Doors"],
            "Market_Category" : request.form["Market_Category"],
            "Vehicle_Style" : request.form["Vehicle_Style"],
            "Price" : request.form["Price"]
        }})
        if new_vehicle.matched_count == 1:
            edited_vehicle_link = "http://localhost:5000/api/v1.0/vehicles/" + id
            return make_response( jsonify({ "URL":edited_vehicle_link } ), 201)
        else:
            return make_response( jsonify({"Error" : "Could not edit Vehicle! Please Try again."} ), 404 )
    
# DELETE A VEHICLE [DELETE]
@app.route("/api/v1.0/vehicles/<string:id>", methods=["DELETE"])
def delete_vehicle(id):
    result = vehicles.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 204 )
    else:
        return make_response( jsonify( { "Error!" : "Invalid Vehicle ID" } ), 404)

#### ADD A VEHICLE REVIEW [POST]
@app.route("/api/v1.0/vehicles/<string:id>/reviews", methods=["POST"])
def add_new_review(id):
    new_review = {
        "_id" : ObjectId(),
        "username" : request.form["username"],
        "comment" : request.form["comment"],
        "stars" : request.form["stars"],
        "date" : request.form["date"]
    }
    vehicles.update_one( { "_id" : ObjectId(id) },
        {
            "$push" : {"reviews" : new_review }
        }
    )
    new_review_link = "http://localhost:5000/api/v1.0/vehicles/" + id + \
        "/reviews/" + str(new_review["_id"])
    return make_response( jsonify( { "URL" : new_review_link} ), 201 )

# RETRIEVE VEHICLE REVIEWS [GET]
@app.route("/api/v1.0/vehicles/<string:id>/reviews", methods=["GET"])
def fetch_all_reviews(id):
    data_to_return = []
    vehicle = vehicles.find_one( \
        { "_id" : ObjectId(id) }, \
        { "reviews" : 1, "_id" : 0 } )
    for review in vehicle["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review) 
    return make_response( jsonify( data_to_return ), 200 )

# RETRIEVE ONE VEHICLE REVIEW [GET]
@app.route("/api/v1.0/vehicles/<string:id>/reviews/<string:review_id>", methods=["GET"])
def fetch_one_review(id, review_id):
    vehicle = vehicles.find_one(
        { "reviews._id" : ObjectId(review_id) },
        { "_id" : 0, "reviews.$" : 1}
    )
    if vehicle is None:
        return make_response( jsonify( {"Error!" : "Invalid Vehicle or Review Id"}), 404 )
    else:
        vehicle["reviews"][0]["_id"] = str(vehicle["reviews"][0]["_id"])
        return make_response(jsonify( vehicle["reviews"][0]), 200)

# EDIT A VEHICLE REVIEW [PUT]
@app.route("/api/v1.0/vehicles/<id>/reviews/<review_id>", methods=["PUT"])
def edit_review(id, review_id):
    edited_review = {
        "reviews.$.username" : request.form["username"],
        "reviews.$.comment" : request.form["comment"],
        "reviews.$.stars" : request.form['stars']
    }
    vehicles.update_one(
        { "reviews._id" : ObjectId(review_id) },
        { "$set" : edited_review } )
    edit_review_url = "http://localhost:5000/api/v1.0/vehicles/" + id + "/reviews/" + review_id
    return make_response( jsonify( {"URL":edit_review_url} ), 200)

# DELETE A VEHICLE REVIEW [DELETE]
@app.route("/api/v1.0/vehicles/<id>/reviews/<review_id>", methods=["DELETE"])
def delete_review(id, review_id):
    vehicles.update_one( { "_id" : ObjectId(id) },
        { "$pull" : { "reviews" : { "_id" : ObjectId(review_id) } } } )
    return make_response( jsonify( {} ), 204)

if __name__ == "__main__":
    app.run( debug = True)
