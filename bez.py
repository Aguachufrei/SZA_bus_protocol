import socket, sys, os
import utils

SERVER = "localhost"
PORT = 41900

class Menua:
    List, Book, Cancel, Exit = range(1, 5)
    Options = (
        "Ikusi zerbitzuak",
        "Egin erreserba",
        "Utzi erreserba",
        "Saioa amaitu"
    )

    def menua():
        print("+{}+".format('-' * 30))
        for i, option in enumerate(Menua.Options, 1):
            print("| {}.- {:<25}|".format(i, option))
        print("+{}+".format('-' * 30))

        while True:
            try:
                selected = int(input("Egin zure aukera: "))
            except:
                print("Aukera okerra, saiatu berriro.")
                continue
            if 0 < selected <= len(Menua.Options):
                return selected
            else:
                print("Aukera okerra, saiatu berriro.")

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
            print("Erabiltzailea ez da ezagutzen, ¿nahi duzu gure zerbitzuan erregistratzea? N/y")
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
        message = "{}#{}\r\n".format(utils.Command.Password, password)
        s.sendall(message.encode("ascii"))
        message = utils.recvline(s).decode("ascii")
        if iserror(message):
            continue
        print("logged in succesfully")
        while True:
            option = Menua.menua()

            if option == Menua.List:
                message = "{}\r\n".format(utils.Command.List)
                s.sendall(message.encode("ascii"))
                response = utils.recvline(s).decode("ascii")
                if iserror(response):
                    print("Errorea zerbitzuak lortzean")
                else:
                    print("Zerbitzuak eskuragarri:", response[3:])

            elif option == Menua.Book:
                geltoki = input("Sartu geltokia: ")
                linea = input("Sartu línea: ")
                ordua = input("Sartu ordua (HH:MM): ")
                message = "{} {} {} {}\r\n".format(utils.Command.Book, geltoki, linea, ordua)
                s.sendall(message.encode("ascii"))
                response = utils.recvline(s).decode("ascii")
                if iserror(response):
                    print("Esandako bidaia ez da aurkitu")
                else:
                    print("Erreserba ondo  correctamente")

            elif option == Menua.Cancel:
                geltoki = input("Sartu geltokia: ")
                linea = input("Sartu línea: ")
                ordua = input("Sartu ordua (HH:MM): ")
                message = "{} {} {} {}\r\n".format(utils.Command.Cancel, geltoki, linea, ordua)
                s.sendall(message.encode("ascii"))
                response = utils.recvline(s).decode("ascii")
                if iserror(response):
                    print("Errorea erreserba ezabatzean")
                else:
                    print("Erreserba ondo ezabatu egin da")

            elif option == Menua.Exit:
                message = "{}\r\n".format(utils.Command.Exit)
                s.sendall(message.encode("ascii"))
                print("Saioa amaitu da.")
                break
        

    s.sendall(utils.Command.NewUser.encode("ascii"))
    utils.recvline(s).decode("ascii")

    # Soket-a itxi
    s.close()
