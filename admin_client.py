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
    

def main():
    print("Welcome to admin client")

    while True:
        answer = input(">>> ")

        if answer == "exit":
            break
        elif answer == "admin":
            admin()
        else:
            print("Unknonw command")
        

if __name__ == "__main__":
    main()