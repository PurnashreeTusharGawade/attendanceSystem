import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime


def show_welcome_screen():
    # Create a blank black image
    welcome_screen = np.zeros((600, 800, 3), dtype=np.uint8)

    # Add text to the welcome screen
    cv2.putText(welcome_screen, "CMR INSTITUTE OF TECHNOLOGY", (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(welcome_screen, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", (140, 150), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 1)
    cv2.putText(welcome_screen, "21CSL66 - Computer Graphics and Image Processing Laboratory", (75, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    cv2.line(welcome_screen, (10, 230), (780, 230), (255, 255, 255), 1)
    cv2.putText(welcome_screen, "MARKING SYSTEM OF ATTENDANCE USING", (70, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(welcome_screen, "IMAGE PROCESSING", (230, 318), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Created By
    cv2.putText(welcome_screen, "Created By", (35, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    cv2.putText(welcome_screen, "Preety Shah (1CR21CS138)", (35, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(welcome_screen, "Purnashree Tushar Gawade (1CR21CS140)", (35, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Guided By
    cv2.putText(welcome_screen, "Guided By", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    cv2.putText(welcome_screen, "Dr. Preethi Sheba Hepsiba, Associate Professor", (400, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                1)
    cv2.putText(welcome_screen, "Mrs. Rajni Tiwari, Assistant professor", (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                1)
    cv2.putText(welcome_screen, "PRESS <<ENTER>> TO BEGIN", (200, 550), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Display the welcome screen
    cv2.imshow('Welcome Screen', welcome_screen)

    while True:
        if cv2.waitKey(1) == 13:  # Enter key
            cv2.destroyWindow('Welcome Screen')
            break


def start_attendance_system():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendancerealtime-385d4-default-rtdb.firebaseio.com/",
        'storageBucket': "faceattendancerealtime-385d4.appspot.com"
    })
    bucket = storage.bucket()

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    target_width = 600
    target_height = 438

    imgBackground = cv2.imread('Resources/background.png')

    # Importing the mode images into a list
    folderModePath = 'Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = []
    for path in modePathList:
        modeImg = cv2.imread(os.path.join(folderModePath, path))
        imgModeList.append(modeImg)

    # Load the encoding file
    print("Loading Encode File ...")
    file = open('EncodeFile.p', 'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown, studentIds = encodeListKnownWithIds
    print("Encode File Loaded")

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    while True:
        success, img = cap.read()
        img_resized = cv2.resize(img, (target_width, target_height))

        imgS = cv2.resize(img_resized, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurrFrame = face_recognition.face_locations(imgS)
        encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

        imgBackground[156:156 + target_height, 47:47 + target_width] = img_resized

        # Resize the mode image to fit into the specified region
        mode_img_width = 414
        mode_img_height = 633
        imgModeResized = cv2.resize(imgModeList[modeType], (mode_img_width, mode_img_height))
        imgBackground[18:18 + mode_img_height, 740:740 + mode_img_width] = imgModeResized

        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(300,300))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1


        if counter != 0:
            if counter == 1:
                #get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #get image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2. imdecode(array,cv2.COLOR_BGRA2BGR)
                imgStudent = cv2.resize(imgStudent, (223,223))
                #update attendance data
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[18:18 + mode_img_height, 740:740 + mode_img_width] = imgModeList[modeType]

            if modeType!=3:
                if 10<counter<20:
                    modeType=2
                    imgBackground[18:18 + mode_img_height, 740:740 + mode_img_width] = imgModeList[modeType]

                if counter<=10:
                    # Adjust coordinates for cv2.putText based on your layout
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (794, 98),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)

                    cv2.putText(imgBackground, str(studentInfo['branch']), (940, 528),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,255,255), 1)
                    cv2.putText(imgBackground, str(id), (935, 470),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['semester']), (901, 583),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255,255,255), 1)
                    cv2.putText(imgBackground, str(studentInfo['sec']), (1010, 583),
                                 cv2.FONT_HERSHEY_COMPLEX, 0.6, (255,255,255), 1)
                    #center align name
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 0.7, 1)
                    offset = (414-w) // 2
                    #print(offset)
                    cv2.putText(imgBackground, str(studentInfo['name']), (740 + offset, 415),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (50, 50, 50), 1)

                    imgBackground[147:147 + 223, 838: 838 + 223] = imgStudent
            counter += 1

            if counter>=20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[18:18 + mode_img_height, 740:740 + mode_img_width] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)
        cv2.waitKey(1)


if __name__ == "__main__":
    show_welcome_screen()
    start_attendance_system()
