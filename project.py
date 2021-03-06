import socket
import sqlite3 as sql
import random
import json
import urllib.parse as trans


def zone_call(request, calls_db):
    if len(request) == 4:
        with calls_db:
            cur = calls_db.cursor()
            cur.execute(f"SELECT * FROM '{trans.unquote(request[2])}'")
            table = cur.fetchall()
            answer = json.dumps(table,ensure_ascii=False)
            answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
            cur.close()
            calls_db.commit()
    else:
        answer = json.dumps("NO")
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)


def token_generator(auth_db):
    a = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"
    token = ""
    for word in range(random.randint(25, 35)):
        token += a[random.randint(0, len(a) - 1)]
    return is_token_exist(token, auth_db)


def is_token_exist(token, auth_db):
    with auth_db:
        cur = auth_db.cursor()
        cur.execute("SELECT token FROM `auth`")
        tokens = cur.fetchall()
        if token in tokens:
            token_generator(auth_db)
        else:
            with open("tokens.txt", "a") as f:
                f.write(f"{token}\n")
            return token


def people_auth(auth_db, request, ids_db):
    with auth_db:
        cur = auth_db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS `auth` (`number` STRING, `name` STRING, 'pwd' STRING,'token' STRING)")
        if len(request) == 6:
            number, name, pwd = request[2], trans.unquote(request[3]), request[4]
            cur.execute("SELECT number FROM `auth`")
            table = cur.fetchall()
            flag = True
            for i in range(len(table)):
                if str(number) == str(table[i][0]):
                    flag = False
                    break
            if flag:
                token = token_generator(auth_db)
                cur.execute(f"INSERT INTO `auth` VALUES ('{str(number)}', '{str(name)}','{str(pwd)}','{str(token)}')")
                answer = json.dumps("YES " + token)
                answer = answer.encode("utf-8")
                with ids_db:
                    curs = ids_db.cursor()
                    curs.execute(
                        f"CREATE TABLE IF NOT EXISTS '{token}' (`mesta` STRING, `otzivi` STRING, 'mark' STRING)")
                    ids_db.commit()
                    curs.close()
            else:
                answer = json.dumps("NO")
                answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
        else:
            answer = json.dumps("NO")
            answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
        auth_db.commit()
        cur.close()


def sign_in(request):
    if len(request) == 5:
        cur = auth_db.cursor()
        number, pwd = request[2], request[3]
        cur.execute("SELECT number,pwd,token FROM `auth`")
        table = cur.fetchall()
        flag = True
        for i in range(len(table)):
            if str(number) == str(table[i][0]):
                flag = False
                if str(pwd) == str(table[i][1]):
                    answer = json.dumps("YES " + table[i][2])
                    answer = answer.encode("utf-8")
                    break
                else:
                    answer = json.dumps("NO")
                    answer = answer.encode('utf-8')
                    break

        if flag:
            answer = json.dumps("NO")
            answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)
        cur.close()
    else:
        answer = json.dumps("NO")
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)


def call_back(request, ids_db, calls_db,auth_db):
    if len(request) == 7:
        token, zone_id, call, mark = request[2], trans.unquote(request[3]), trans.unquote(request[4]), request[5]
        with calls_db:
            with auth_db:
                cur1 = auth_db.cursor()
                cur1.execute(f'SELECT number,name FROM "auth" WHERE token="{token}"')
                number = cur1.fetchall()
                auth_db.commit()
                cur1.close()
            cur = calls_db.cursor()
            cur.execute(f"SELECT number FROM `{zone_id}`")
            table = cur.fetchall()
            for i in range(len(table)):
                if str(table[i][0]) == str(f'{number[0][0]} {number[0][1]}'):
                    cur.execute(f"DELETE FROM '{zone_id}' WHERE number=''{number[0][0]} {number[0][1]}'")
                    break
            cur.execute(f"INSERT INTO `{zone_id}` VALUES ('{number[0][0]} {number[0][1]}', '{str(call)}', '{mark}')")
            calls_db.commit()
            cur.close()
        with ids_db:
            cur = ids_db.cursor()
            cur.execute(f"SELECT mesta FROM `{token}`")
            table = cur.fetchall()
            for i in range(len(table)):
                if str(table[i][0]) == str(zone_id):
                    cur.execute(f"DELETE FROM '{token}' WHERE mesta='{zone_id}'")
                    break
            cur.execute(
                f"INSERT INTO `{token}` VALUES ('{str(zone_id)}', '{str(call)}', '{mark}')")  ## ???? ???????????? ?????????????????????? ?????????????????????????? ?????????? ???????????????????? ?????????? ??????
            ids_db.commit()
            cur.close()

        answer = json.dumps("YES")
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)
    else:
        answer = json.dumps("NO")
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)


def my_calls(request, ids_db):
    if len(request) == 4:
        with ids_db:
            cur = ids_db.cursor()
            token = request[2]
            cur.execute(f"SELECT * FROM '{token}'")
            table = cur.fetchall()
            answer = json.dumps(table,ensure_ascii=False)
            answer = answer.encode("utf-8")
            client.send(HDRS.encode('utf-8') + answer)
            ids_db.commit()
            cur.close()
    else:
        answer = json.dumps("NO")
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)


def delete_call(request, ids_db, calls_db):
    if len(request) == 5:
        with ids_db:
            cur = ids_db.cursor()
            token, zone_id = request[2], trans.unquote(request[3])
            with auth_db:
                cur1 = auth_db.cursor()
                cur1.execute(f'SELECT number,name FROM "auth" WHERE token="{token}"')
                number = cur1.fetchall()
                auth_db.commit()
                cur1.close()
            cur.execute(f"SELECT mesta FROM `{token}`")
            table = cur.fetchall()
            for i in range(len(table)):
                if str(zone_id) == str(table[i][0]):
                    cur.execute(f"DELETE FROM '{token}' WHERE mesta='{zone_id}'")
                    break
            ids_db.commit()
            cur.close()
        with calls_db:
            cur = calls_db.cursor()
            token, zone_id = request[2], trans.unquote(request[3])
            cur.execute(f"SELECT number FROM `{zone_id}`")
            table = cur.fetchall()

            for i in range(len(table)):
                if str(f'{number[0][0]} {number[0][1]}') == str(table[i][0]):
                    cur.execute(f"DELETE FROM '{zone_id}' WHERE number='{number[0][0]} {number[0][1]}'")
                    break
            answer = json.dumps('YES').encode("utf-8")
            client.send(HDRS.encode('utf-8') + answer)
            calls_db.commit()
            cur.close()
    else:
        answer = 'NO'.encode("utf-8")
        client.send(HDRS.encode('utf-8') + answer)

def zone_finder(request,zones_db):
    if len(request) == 4:
        find = trans.unquote(request[2])
        good_news = []
        with zones_db:
            cur = zones_db.cursor()
            cur.execute("SELECT * FROM 'zone'")
            table = cur.fetchall()
            for i in table:
                if find.lower() in i[0].lower():
                    good_news.append(i)
            answer = json.dumps(good_news,ensure_ascii=False)
            answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
            zones_db.commit()
            cur.close()

    else:
        answer = json.dumps('NO')
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)

def interesting_places(request,zones_db):
    if len(request) == 3:
        with zones_db:
            cur = zones_db.cursor()
            cur.execute("SELECT * FROM 'zone'")
            table = cur.fetchall()
            answer = json.dumps(table,ensure_ascii=False)
            answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
            zones_db.commit()
            cur.close()
    else:
        answer = json.dumps('NO')
        answer = answer.encode('utf-8')
        client.send(HDRS.encode('utf-8') + answer)

server = socket.create_server(("0.0.0.0", 6677))
server.listen(50)
otzyvs_db = sql.connect('calls.db')
zones_db = sql.connect("zones.db")
while True:
    try:
        try:
            client, adress = server.accept()
            data = client.recv(1024).decode('utf-8')
            HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
            request = data.split()[1].split("/")
            cmd = request[1]
            auth_db = sql.connect('auth.db')
            ids_db = sql.connect('ids.db')
            calls_db = sql.connect('calls.db')
            commands = ["AUTH", "SIGNIN", "CALLBACK", "MYCALLS", "DELETE", "ZONECALL","FINDZONE","MAIN"]
            if cmd == commands[0]:
                people_auth(auth_db, request, ids_db)
            elif cmd == commands[1]:
                sign_in(request)
            elif cmd == commands[2]:
                call_back(request, ids_db, calls_db,auth_db)
            elif cmd == commands[3]:
                my_calls(request, ids_db)
            elif cmd == commands[4]:
                delete_call(request, ids_db, calls_db)
            elif cmd == commands[5]:
                zone_call(request, calls_db)
            elif cmd == commands[6]:
                zone_finder(request, zones_db)
            elif cmd == commands[7]:
                interesting_places(request,zones_db)
            client.shutdown(socket.SHUT_WR)
        except Exception:
            answer = json.dumps("Nice try")
            answer = answer.encode('utf-8')
            client.send(HDRS.encode('utf-8') + answer)
            client.shutdown(socket.SHUT_WR)
            continue
    except KeyboardInterrupt:
        server.close()
        break
    """""""""
    main_bd = sql.connect('ids.db')
    with main_bd:
        cur = main_bd.cursor()
        #cur.execute("DELETE FROM auth WHERE number='7'")
        cur.execute(f"SELECT * FROM '{request[2]}'")
        current_table = cur.fetchall()
        print(current_table)
        main_bd.commit()
        cur.close()
    #####   res = curs.execute("SELECT name FROM sqlite_master WHERE type='table';") ##### ???????????????? ???????? ????????????
    ##for name in res:
    ##    print(name[0])"""""
