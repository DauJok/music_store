from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient


app = Flask(__name__)
api = Api(app)

# Database instance
client = MongoClient("mongodb://my_mongo_db:27017")
db = client.storeDB

records = db["Records"]


retrieve_put_args = reqparse.RequestParser()

retrieve_put_args.add_argument(
    "artist", type=str, help="Music artist", required=True)
retrieve_put_args.add_argument(
    "year", type=int, help="Year that vinyl was published", required=True)
retrieve_put_args.add_argument(
    "title", type=str, help="Vinyl's title", required=True)
retrieve_put_args.add_argument(
    "price", type=float, help="Vinyl's price")
retrieve_put_args.add_argument(
    "stock", type=int, help="Is vinyl in stock")
retrieve_put_args.add_argument(
    "publisher", type=str, help="Publishing company")
retrieve_put_args.add_argument(
    "description", type=str, help="Record's description")


def recordExists(vinyl_id):
    """Checks if vinyl_id already exists in database"""
    if records.find({"vinyl_id": vinyl_id}).count() == 0:
        return False
    else:
        return True


def dataRead(vinyl_id):
    return [doc for doc in records.find({"vinyl_id": vinyl_id})]

# CREATE #
class Register(Resource):
    def put(self, vinyl_id):

        if recordExists(vinyl_id):
            retJson = {
                "status": 301,
                "msg": "Record already exists"
            }
            return jsonify(retJson)

        # parse posted data
        args = request.get_json()
        artist = args["artist"]
        year = args["year"]
        title = args["title"]
        price = args["price"]
        stock = args["stock"]
        publisher = args["publisher"]
        description = args["description"]

        # insert record
        records.insert_one({
            "vinyl_id": vinyl_id,
            "artist": artist,
            "year": year,
            "title": title,
            "price": price,
            "stock": stock,
            "publisher": publisher,
            "description": description
        })

        retJson = {
            "status": 200,
            "msg": "Successful post"
        }
        return jsonify(retJson)

# READ #
class Retrieve(Resource):
    def get(self, vinyl_id):

        if not recordExists(vinyl_id):
            retJson = {
                "status": 301,
                "msg": "Invalid record"
            }
            return jsonify(retJson)

        dat = dataRead(vinyl_id)
        print(dat)
        retJson = {
            "status": 200,
            "obj": dat
        }

        return jsonify(retJson)

# UPDATE #
class Save(Resource):
    def post(self, vinyl_id):

        if not recordExists(vinyl_id):
            retJson = {
                "status": 404,
                "msg": "Invalid record"
            }
            return jsonify(retJson)


        args = request.get_json()

        to_update = {}

        for i, (k,v) in enumerate(args.items()):
            if v == None:
                pass
            else:
                to_update[k] = v

        records.update(
        {"vinyl_id": vinyl_id},
        { '$set': {to_update} })


        retJson = {
            "status": 201,
            "msg": "Successful update"
        }
        return jsonify(retJson)

# DELETE #
class Delete(Resource):
    def delete(self, vinyl_id):
        if not recordExists(vinyl_id):
            retJson = {
                "status": 404,
                "msg": "Record does'n exists"
            }
            return jsonify(retJson)

        records.deleteOne({"vinyl_id": vinyl_id})

        retJson = {
            "status": 200,
            "msg": "Record deleted successfully"
        }
        return jsonify(retJson)


# GET ALL #
class Mash(Resource):
    def get(self):
        retJson = {
                "status": 200,
                "obj": [ doc for doc in records.find({}).limit(10) ]
        }
        return jsonify(retJson)

api.add_resource(Register, "/discs/<int:vinyl_id>")
api.add_resource(Retrieve, "/discs/<int:vinyl_id>")
api.add_resource(Save, "/discs/<int:vinyl_id>")
api.add_resource(Delete, "/discs/<int:vinyl_id>")
api.add_resource(Mash, "/home")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
