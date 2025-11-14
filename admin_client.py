import requests
import url_info

URL = url_info.FULL_URL

print(URL)

class Config:
    SOME = 10


def admin():
    token = input("input token: ")
    data = {"token": token}
    response = requests.post(URL + "/admin", json=data)
    print(response.text)


def clear_upload():
    token = input("input token: ")
    data = {"token": token}
    response = requests.post(URL + "/admin/clear_uploads", json=data)
    print(response.text)


def list_uploads():
    token = input("input token: ")
    data = {"token": token}
    response = requests.post(URL + "/admin/list_uploads", json=data)
    print(response.text)


def log():
    token = input("input token: ")
    data = {"token": token}
    response = requests.post(URL + "/admin/log", json=data)
    print(response.text)


def main():
    print("Welcome to admin client")
    while True:
        answer = input(">>> ")
        if answer == "exit":
            break
        elif answer == "admin":
            admin()
        elif answer == "clear_uploads":
            clear_upload()
        elif answer == "list_uploads":
            list_uploads()
        elif answer == "log":
            log()
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()