import socket, sys, os, signal, hashlib, datetime
import utils


PORT = 41900
DATA_PATH = "data.txt"
USERS_PATH = "users.txt"


class State:
    Identification, Authentication, Creation, Main, Booking = range(5)


def sendOK(s, params=""):
    s.sendall(("OK\r\n").encode("ascii"))


def sendER(s, code=1):
    s.sendall(("ER{}\r\n".format(code)).encode("ascii"))


def hash_password(password):
    return hashlib.sha512(password.encode()).hexdigest()


def save_user(username, password):
    with open(USERS_PATH, "a", encoding="utf-8") as f:
        f.write(f"{username}#{password}\n")


def load_users(filename):
    users = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            user, pwd_hash = line.split("#", 1)
            users[user] = pwd_hash
    return users


def load_data(filename):
    data = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            station_name, information = line.split("#", 1)
            entries = information.split("#")
            data[station_name] = {}
            for entry in entries:
                entry = entry.strip()
                part = entry.split(" ")
                timepart = part[1].split(":")
                entry_data = {
                    "first": datetime.time(int(timepart[0]), int(timepart[1])),
                    "freq": int(part[2]),
                }
                data[station_name][part[0]] = entry_data
    return data


user_rg = load_users(USERS_PATH)
data_rg = load_data(DATA_PATH)
print(data_rg)
print()
print(data_rg["GELTOKI1"])
print(data_rg["GELTOKI1"]["35"])
print(data_rg["GELTOKI1"]["35"]["freq"])


def session(s):
    state = State.Identification
    username = None
    while True:
        message = utils.recvline(s).decode("ascii")
        print(message)
        print(state)
        if not message:
            return

        if message.startswith(utils.Command.User):
            if state != State.Identification:
                sendER(s)
                continue
            username = message[5:]
            if username not in user_rg:
                sendER(s)
                print("user is not registered")
            sendOK(s)
            state = State.Authentication

        elif message.startswith(utils.Command.Password):
            if state != State.Authentication:
                sendER(s)
                continue
            password = hash_password(message[5:])
            if user_rg.get(username).strip() == password.strip():
                sendOK(s)
                print("logged in succesfully")
                state = State.Main
                continue
            sendER(s, 3)
            print("passwords do not match")
            state = State.Identification

        elif message.startswith(utils.Command.NewUser):
            """
            if state != State.Identification:
                sendER(s)
                continue
                """
            username = message[5:]
            print(username)
            if username in user_rg:
                sendER(s)
                print("user already exists")
            sendOK(s)
            state = State.Creation

        elif message.startswith(utils.Command.NewPassword):
            print(state)
            if state != State.Creation:
                sendER(s)
                continue
            password = hash_password(message[5:])
            save_user(username, password)
            user_rg[username] = password
            sendOK(s)
            state = State.Main
        elif message.startswith(utils.Command.Exit):
            sendOK(s)
            return

        else:
            sendER(s)
            print("Unknown command")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(("", PORT))
    s.listen(5)

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        dialog, address = s.accept()
        print("Konexioa ezarrita {0[0]}:{0[1]} socketarekin.".format(address))
        if os.fork():
            dialog.close()
        else:
            s.close()
            session(dialog)
            dialog.close()
            exit(0)
