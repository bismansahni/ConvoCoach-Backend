# import firebase_admin
# from firebase_admin import credentials, firestore
#
# if not firebase_admin._apps:
#     cred = credentials.Certificate("service-key.json")
#     firebase_admin.initialize_app(cred)
#
# db = firestore.client()





import firebase_admin
from firebase_admin import credentials, firestore, storage

# Initialize Firebase only if it hasn't been initialized already
if not firebase_admin._apps:
    cred = credentials.Certificate("service-key.json")  # Path to your service account file
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ai-interviewer-9aeea.appspot.com'  # Your Firebase Storage bucket name
    })

# Initialize Firestore client
db = firestore.client()

# Initialize Firebase Storage bucket (this will be shared across your app)
bucket = storage.bucket()
