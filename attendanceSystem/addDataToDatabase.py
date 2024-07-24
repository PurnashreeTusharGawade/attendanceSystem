import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-385d4-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "1CR21CS125":
        {
            "name" : "Piddaparthy Harshitha",
            "branch" : "CSE",
            "semester" : 6,
            "sec" : 'B',
            "starting_year":2021,
            "total_attendance" : 6,
            "last_attendance_time" : "2024-07-21 00:54:34"
        },
    "1CR21CS138":
            {
                "name" : "Preety Shah",
                "branch" : "CSE",
                "semester" : 6,
                "sec" : 'B',
                "starting_year":2021,
                "total_attendance" : 6,
                "last_attendance_time" : "2024-07-21 00:54:34"
            },
    "1CR21CS140":
            {
                "name" : "Purnashree Tushar Gawade",
                "branch" : "CSE",
                "semester" : 6,
                "sec" : 'B',
                "starting_year":2021,
                "total_attendance" : 6,
                "last_attendance_time" : "2024-07-21 00:54:34"
            }
}

for key,value in data.items():
    ref.child(key).set(value)