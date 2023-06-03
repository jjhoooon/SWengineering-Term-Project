import pymongo
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)

cluster=MongoClient("mongodb+srv://woalsdl7399:driermine7399@cluster0.wzjt024.mongodb.net/?retryWrites=true&w=majority")
db = cluster["SW_term_project"]
# collection = db["zzam"]

post={"_id":1,"name":"zam","score":100}

db.zzam.delete_one({'_id':1})