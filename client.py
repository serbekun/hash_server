import requests
import json

URL = "http://192.168.3.19:2222"

def base64_client():
    try:
        text = input("Input text: ")
        print("1: Encode")
        print("2: Decode")
        mod = input("Select mode (1 or 2): ")
        
        data = {"text": text, "mod": mod}
        response = requests.post(URL + "/base64", json=data, timeout=10)
        
        if response.status_code == 200:
            print("Result:", response.text)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")

if __name__ == "__main__":
    base64_client()