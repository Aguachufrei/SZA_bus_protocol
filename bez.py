import socket, sys, os
import utils

SERVER = "localhost"
PORT = 41900


def iserror(message):
    if message.startswith("ER"):
        code = int(message[2:])
        # print( ER_MSG[code] )
        return True
    else:
        return False


def int2bytes(n):
    if n < 1 << 10:
        return str(n) + " B  "
    elif n < 1 << 20:
        return str(round(n / (1 << 10))) + " KiB"
    elif n < 1 << 30:
        return str(round(n / (1 << 20))) + " MiB"
    else:
        return str(round(n / (1 << 30))) + " GiB"


if __name__ == "__main__":
    # Soket-a ireki
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))

    # Saioa hasi
    while True:
        user = input("Erabiltzaile izena: ")
        message = "{}#{}\r\n".format(utils.Command.User, user)
        s.sendall(message.encode("ascii"))
        message = utils.recvline(s).decode("ascii")
        if iserror(message):
            print(
                "Erabiltzailea ez da ezagutzen, ¿nahi duzu gure zerbitzuan erregistratzea? N/y\n"
            )
            erantzuna = input("> ")
            if erantzuna.lower() == "y":
                user = input("Erabiltzaile berria: \n")
                message = "{}#{}\r\n".format(utils.Command.NewUser, user)
                s.sendall(message.encode("ascii"))
                message = utils.recvline(s).decode("ascii")
                if iserror(message):
                    print("errorea erabiltzailea sortzen")
                    continue
                password = input("Pasahitza berria: \n")
                message = "{}#{}\r\n".format(utils.Command.NewPassword, password)
                s.sendall(message.encode("ascii"))
                message = utils.recvline(s).decode("ascii")
                if iserror(message):
                    print("errorea erabiltzailea sortzen")
                    continue
                break
            else:
                continue
        password = input("Pasahitza: ")
        message = "{}{}\r\n".format(utils.Command.Password, password)
        s.sendall(message.encode("ascii"))
        message = utils.recvline(s).decode("ascii")
        if iserror(message):
            continue
        break

    print(user, password)
    # Soket-a itxi
    s.close()
