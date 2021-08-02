import pandas as pd # raw dataset
from surprise import SVD, accuracy # SVD model, 평가
from surprise import Reader, Dataset # SVD model의 dataset
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from firebase_admin import db

# server.py : 연결해 1 보낼 수 있음.
import socket

cred = credentials.Certificate("bike-71038-firebase-adminsdk-9kaha-3fa2feb653.json")
firebase_admin.initialize_app(cred, {
      "projectId": "bike-71038"
})
while(1):
    host = '192.168.219.106'  # 호스트 ip를 적어주세요
    port = 1991  # 포트번호를 임의로 설정해주세요

    server_sock = socket.socket(socket.AF_INET)
    server_sock.bind((host, port))
    server_sock.listen(1)

    print("기다리는 중")
    client_sock, addr = server_sock.accept()

    print('Connected by', addr)

    FrameStared = ["", "", "", ""]
    Stars = ["", "", "", ""]
    for i in range(0, 3):
        client_sock.send(str("next").encode("utf-8"))
        data = client_sock.recv(1024)
        print(data.decode("utf-8"), len(data))
        FrameStared[i] = data.decode("utf-8")
        FrameStared[i] = FrameStared[i][2:]
        data = "";
        client_sock.send(str("next").encode("utf-8"))
        data = client_sock.recv(1024)
        print(data.decode("utf-8"), len(data))
        Stars[i] = data.decode("utf-8")
        Stars[i] = Stars[i][2:]
        print(FrameStared[i] + " " + Stars[i])



        data = "";


    db = firestore.client()
    users_ref = db.collection(u'frame')
    query_ref = users_ref.where(u'name', u'==', u'치넬리 벨트릭스')
    docs = users_ref.stream()
    frameNames = []

    for doc in docs:
        frameNames.append(doc.to_dict()['name'])

    f = open("movie_rating.csv", 'r', encoding='utf-8')
    wr = csv.reader(f)
    lines = []
    for line in wr:
        if line[0] != 'Tester':
            lines.append(line)
    f = open('movie_rating.csv', 'w', newline='', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerows(lines)
    f.close()

    f = open("movie_rating.csv", 'a', newline='', encoding='utf-8')
    wr = csv.writer(f)
    for i in range(0, FrameStared.__len__() - 1):
        wr.writerow(['Tester', FrameStared[i], Stars[i]])
    f.close()

    rating = pd.read_csv("movie_rating.csv", encoding='utf-8')
    rating.head()  # critic(user)   title(item)   rating
    rating['critic'].value_counts()
    rating['title'].value_counts()
    tab = pd.crosstab(rating['critic'], rating['title'])
    rating_g = rating.groupby(['critic', 'title'])
    rating_g.sum()
    tab = rating_g.sum().unstack()  # 행렬구조로 변환

    tab.to_csv("mygoal.csv", encoding='utf-8')

    reader = Reader(rating_scale=(1.0, 5.0))  # 평점 범위
    data = Dataset.load_from_df(df=rating, reader=reader)
    train = data.build_full_trainset()  # 훈련셋
    test = train.build_testset()  # 검정셋

    model = SVD(n_factors=100, n_epochs=20, random_state=123)
    model.fit(train)  # model 생성
    user_id = 'Tester'  # 추천대상자
    item_ids = frameNames  # 추천 대상 프레임
    actual_rating = 0  # 실제 평점

    predictValues = []
    for item_id in item_ids:
        predictValues.append(model.predict(user_id, item_id, actual_rating))
    print(predictValues.sort(key=lambda x: -x[3]))
    print(predictValues)


    # print(data2.encode())
    client_sock.send(str(predictValues[0][1]).encode("utf-8"))
    time.sleep(0.1)
    client_sock.send(str(predictValues[1][1]).encode("utf-8"))
    time.sleep(0.1)
    client_sock.send(str(predictValues[2][1]).encode("utf-8"))

    client_sock.close()
    server_sock.close()

