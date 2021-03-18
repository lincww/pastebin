#!/usr/env/bin python3
# encoding:utf-8
import flask
import sqlite3
import json
import random


app = flask.Flask(__name__)


def generate_random_str(randomlength):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def createDatabase():
    sqlconn = sqlite3.connect('database.db')
    sqlconn.execute("""CREATE TABLE code(
        ID INT PRIMARY KEY,
        CODES TEXT,
        ALTERNAME TEXT
        )
        """)
    sqlconn.commit()
    sqlconn.close()


def writeToDatabase(codes, altername):
    sqlconn = sqlite3.connect('database.db')
    sqlconn.execute("INSERT INTO CODE VALUES (NULL,?,?)", (codes, altername))
    sqlconn.commit()
    sqlconn.close()


def checkFromDatabase(altername):
    sqlconn = sqlite3.connect('database.db')
    cur = sqlconn.execute(
        "SELECT CODES FROM CODE WHERE ALTERNAME=?", (altername,))
    data = cur.fetchall()
    if len(data) == 0:
        return {"status": "notFound"}
    elif len(data) == 1:
        return {"status": "ok", "code": data[0][0]}
    else:
        raise IOError


@app.route("/")
def index():
    return flask.render_template('index.html')


@app.route("/postcode", methods=['POST'])
def postCode():
    data = json.loads(flask.request.data)
    code = data['codes']
    altername = data['altername']
    if altername == "":
        altername = generate_random_str(8)
    # Check if have already altername
    status = checkFromDatabase(altername)["status"]
    if status == "notFound":
        writeToDatabase(code, altername)
        return {"status": "ok", "altername": altername}
    else:
        return {"status": "Error", "why": "The altername has been used."}
        # TODO 这里有一个问题是可能随机生成的也会被判断为已被使用，在UX方面不太行，不过需要加一点逻辑，先这样吧，回头再修。反正概率不高。


@app.route("/view/<altername>")
def view(altername):
    data = checkFromDatabase(altername)
    if data["status"] != "ok":
        flask.abort(404)
    else:
        return flask.render_template("view.html", code=data["code"])


@app.route("/raw/<altername>")
def viewRaw(altername):
    data = checkFromDatabase(altername)
    if data["status"] != "ok":
        flask.abort(404)
    else:
        return data["code"]


if __name__ == "__main__":
    createDatabase()
