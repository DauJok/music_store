from flask import Flask, json, request, Response
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
api = Api(app)

# Database instance
client = MongoClient("mongodb://my_mongo_db:27017")
db = client.storeDB

records = db["Records"]


records.insert_many([
{
    "artist": "John Lennon",
    "year": 1980,
    "title": "Double Fantasy",
    "price": 15.0,
    "stock": 5,
    "publisher": "Beatles records",
    "description": "double trouble"
},
{
    "artist": "Yoko Ono",
    "year": 1984,
    "title": "Milk and Honey",
    "price": 27.9,
    "stock": 8000,
    "publisher": "Capitol Records",
    "description": "Double Trouble"
},
{
    "artist": "The Beatles",
    "year": 1969,
    "title": "Abbey Road",
    "price": 72.0,
    "stock": 5,
    "publisher": "Calderstone Records",
    "description": "C'est la Vie!"
}
])

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

def recordExists(artist, year, title):
    if records.find({ '$and': [{"artist": artist}, {"year": year}, {"title": title}] }).count() == 0:
        return False
    else:
        return True

def dataCheck(album_id):
    if records.find({'_id': ObjectId(album_id)}).count() == 0:
        return False
    return True

def dataRead(album_id):
    record = records.find({'_id': ObjectId(album_id)})
    return [{item: data[item] if item != "_id" else str(data[item]) for item in data} for data in record]

# CREATE #
class Create(Resource):
    def post(self):
        # parse posted data
        args = request.get_json()

        if args == {} or args is None:
            return Response(
                response=json.dumps({"Error": "No information provided"}),
                status=400,
                mimetype="application/json")

        if recordExists(args["artist"], args["year"], args["title"]):
            return Response(
                response=json.dumps({"Error": "Conflict, album already exists"}),
                status=409,
                mimetype="application/json")

        Ins_id = records.insert_one( {item: args[item] for item in args if args[item] is not None} )
        success = {
            "Status": "Successfully Created",
            "Album_ID": str(Ins_id.inserted_id)}

        return Response(
            response=json.dumps(success),
            status=201,
            mimetype="application/json",
            headers={"Location":'/albums/{}'.format(Ins_id.inserted_id)} )

# READ #
class Retrieve(Resource):
    def get(self, album_id):

        args = request.get_json()

        if args == {} or args is None and album_id is None:
            return Response(
                response=json.dumps({"Error": "No information provided"}),
                status=400,
                mimetype="application/json")

        if records.find({'_id': ObjectId(album_id)}).count() == 0:
            return Response(
                response=json.dumps({"Error": "Album doesn't exist"}),
                status=404,
                mimetype="application/json")
            

        dat = dataRead(album_id)
        return Response(
            response=json.dumps(dat),
            status=200,
            mimetype="application/json")

# UPDATE #
class Update(Resource):
    def put(self, album_id):

        args = request.get_json()

        if args == {} or args is None:
            return Response(
                response=json.dumps({"Error": "No information provided"}),
                status=400,
                mimetype="application/json")

        if not dataCheck(album_id):
            return Response(
                response=json.dumps({"Error": "Album doesn't exist"}),
                status=404,
                mimetype="application/json")

        Ups_id = records.update_one({'_id': ObjectId(album_id)},
        { '$set': {item: args[item] for item in args if args[item] is not None or item != "_id"} })
            
        return Response(
            response=json.dumps({"Status": "Successfully Updated"}),
            status=200,
            mimetype="application/json",
            headers={"Location":'/albums/{}'.format(album_id)} )


# DELETE #
class Delete(Resource):
    def delete(self, album_id):
        if not dataCheck(album_id):
            return Response(
                response=json.dumps({"Error": "Album doesn't exist"}),
                status=404,
                mimetype="application/json")

        records.delete_one({'_id': ObjectId(album_id)})

        return Response(
            response=json.dumps({"Status": "Successfully Deleted"}),
            status=200,
            mimetype="application/json")


# GET ALL #
class Mash(Resource):
    def get(self):
        documents = records.find().limit(8)
        return Response(
            response=json.dumps(
                [{item: data[item] if item != "_id" else str(data[item]) for item in data} for data in documents]),
            status=200,
            mimetype="application/json")


api.add_resource(Create, "/albums")
api.add_resource(Retrieve, "/albums/<string:album_id>")
api.add_resource(Update, "/albums/<string:album_id>")
api.add_resource(Delete, "/albums/<string:album_id>")
api.add_resource(Mash, "/albums")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
