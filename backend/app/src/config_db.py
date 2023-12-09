import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://paa-projeto-default-rtdb.firebaseio.com/"
})


projetoPAA = db
