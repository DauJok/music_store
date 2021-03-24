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
retrieve_put_args.add_argument(
    "album_id", type=int, help="Album Identificator")

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

        if dataCheck(album_id):
            return Response(
                response=json.dumps({"Error": "Album doesn't exist"}),
                status=404,
                mimetype="application/json")

        to_update = {}

        for i, (k,v) in enumerate(args.items()):
            if v == None:
                pass
            else:
                to_update[k] = v

        Ups_id = records.update_one({'_id': ObjectId(album_id)},
        { '$set': {item: args[item] for item in args if args[item] is not None or item != "_id"} })

        success = {
            "Status": "Successfully Updated",
        return Response(
            response=json.dumps(success),
            status=200,
            mimetype="application/json",
            headers={"Location":'/albums/{}'.format(album_id)} )


# DELETE #
class Delete(Resource):
    def delete(self, album_id):
        if dataCheck(album_id):
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
        documents = records.find().limit(5)
        return Response(
            response=json.dumps([{item: data[item] if item != "_id" else str(data[item]) for item in data} for data in documents]),
            status=200,
            mimetype="application/json")


api.add_resource(Create, "/albums", "/albums/<string:album_id>")
api.add_resource(Retrieve, "/albums","/albums/<string:album_id>")
api.add_resource(Update, "/albums", "/albums/<string:album_id>")
api.add_resource(Delete, "/albums", "/albums/<string:album_id>")
api.add_resource(Mash, "/catalogue")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
