import pandas as pd # raw dataset
from surprise import SVD, accuracy # SVD model, 평가
from surprise import Reader, Dataset # SVD model의 dataset
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from firebase_admin import db
import random
import string
# server.py : 연결해 1 보낼 수 있음.
import socket

cred = credentials.Certificate("bike-71038-firebase-adminsdk-9kaha-3fa2feb653.json")
firebase_admin.initialize_app(cred, {
      "projectId": "bike-71038"
})
while(1):
    host = '192.168.219.100'  # 호스트 ip를 적어주세요
    port = 1991  # 포트번호를 임의로 설정해주세요

    server_sock = socket.socket(socket.AF_INET)
    server_sock.bind((host, port))
    server_sock.listen(1)

    print("기다리는 중")
    client_sock, addr = server_sock.accept()

    print('Connected by', addr)


    productStared = ["", "", "", "", "", ""]
    Stars = ["", "", "", "", "", ""]
    productTypes = client_sock.recv(1024)
    productType = productTypes.decode('utf-8')[2:]
    print(productType)
    for i in range(0, 5):
        client_sock.send(str("next").encode("utf-8"))
        data = client_sock.recv(1024)
        productStared[i] = data.decode("utf-8")
        productStared[i] = productStared[i][2:]
        data = "";
        client_sock.send(str("next").encode("utf-8"))
        data = client_sock.recv(1024)
        Stars[i] = data.decode("utf-8")
        Stars[i] = Stars[i][2:]
        print(productStared[i] + " " + Stars[i])
        data = "";

    print("wwoow")
    db = firestore.client()

    users_ref = db.collection(productType)
    #query_ref = users_ref.where(u'name', u'==', u'치넬리 벨트릭스')
    docs = users_ref.stream()
    productNames = []

    for doc in docs:
        productNames.append(doc.to_dict()['name'])

    f = open(productType+"_rating.csv", 'r', encoding='utf-8')
    wr = csv.reader(f)
    lines = []
    for line in wr:
        if line[0] != 'Tester':
            lines.append(line)
    f = open(productType+"_rating.csv", 'w', newline='', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerows(lines)
    f.close()

    f = open(productType+"_rating.csv", 'a', newline='', encoding='utf-8')
    wr = csv.writer(f)
    for i in range(0, productStared.__len__() - 1):
        wr.writerow(['Tester', productStared[i], Stars[i]])
    result = ""
    for i in range(5) :
        result += random.choice(string.ascii_letters)
    for i in range(0, productStared.__len__() - 1):
        wr.writerow(['Tester'+result, productStared[i], Stars[i]])
    f.close()

    rating = pd.read_csv(productType+"_rating.csv", encoding='utf-8')
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
    item_ids = productNames  # 추천 대상 프레임
    actual_rating = 0  # 실제 평점

    predictValues = []
    for item_id in item_ids:
        predictValues.append(model.predict(user_id, item_id, actual_rating))
    modifiedValues = []
    for i in predictValues:
        for j in range(0,5):
            if( productStared[j] == i[1]):
                print(i[3])
                print(float(Stars[j]))
                modifiedValues.append((productStared[j],(i[3] + float(Stars[j])) / 2.0))

    for j in range(0, 5):
        print(modifiedValues[j][0])
    print(modifiedValues.sort(key=lambda x: -x[1]))
    print(modifiedValues)


    # print(data2.encode())
    client_sock.send(str(modifiedValues[0][0]).encode("utf-8"))
    time.sleep(0.1)

    client_sock.close()
    server_sock.close()

