from flask import Flask
from flask import request
from flask import jsonify
import pymysql

app = Flask(__name__)
connection = pymysql.connect(host='localhost',
                             user='zhenqi',
                             password='Jankee19920808',
                             db='iems5722',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def hello_world():
    return "Hello world!"


@app.route('/api/a3/get_chatrooms')
def get_chatrooms():
    # Get the list of chat rooms from mysql.
    result = {}
    connection.ping(reconnect = True)
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM chatrooms")
        result["data"] = cur.fetchall()
        result["status"] = "OK"
        # print(result)
    return jsonify(result)


@app.route('/api/a3/get_messages', methods=['GET'])
def get_messages():
    # Get the list of messages of a certain chat room from mysql.
    chatroom_id = int(request.args.get('chatroom_id'))
    page = int(request.args.get('page'))

    result = {}
    connection.ping(reconnect = True)
    with connection.cursor() as cur:
        query = "SELECT COUNT(`message`) FROM `messages` WHERE `chatroom_id` = %s"
        cur.execute(query, (chatroom_id,))
        num_of_messages = cur.fetchall()[0]["COUNT(`message`)"]
        # print(num_of_messages)
        if page > (num_of_messages + 4) // 5 or page <= 0:
            result["status"] = "ERROR"
        else:
            result["data"] = {}
            result["data"]["current_page"] = page
            query = "SELECT `message`, `name`, `message_time`, `user_id` FROM `messages` WHERE `chatroom_id` = %s " \
                    "ORDER BY `message_time` DESC LIMIT %s, 5"
            cur.execute(query, (chatroom_id, (page - 1) * 5))
            result["data"]["messages"] = []
            for m in cur.fetchall():
                m["message_time"] = m["message_time"].strftime("%Y-%m-%d %H:%M")
                result["data"]["messages"].append(m)
                # print(m)
            result["data"]["total_pages"] = (num_of_messages + 4) // 5
            result["status"] = "OK"

    return jsonify(result)


@app.route('/api/a3/send_message', methods=['POST'])
def send_message():
    # Receive the message and store it into mysql.
    chatroom_id = int(request.form.get("chatroom_id", "-1"))
    user_id = int(request.form.get("user_id", "-1"))
    name = request.form.get("name", "")
    message = request.form.get("message", "")

    result = {}

    if chatroom_id == -1 or user_id == -1 or name == "" or message == "":
        result["status"] = "ERROR"
    else:
        result["status"] = "OK"
        connection.ping(reconnect = True)
        with connection.cursor() as cur:
            query = "INSERT INTO `messages` (`chatroom_id`, `user_id`, `name`, `message`) VALUES (%s, %s, %s, %s)"
            cur.execute(query, (chatroom_id, user_id, name, message))

        connection.commit()

    return jsonify(result)


# app.debug = True
# app.run()
