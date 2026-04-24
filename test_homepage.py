import requests


def main():
    try:
        response = requests.get('http://127.0.0.1:8000/')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Homepage is working!")
        else:
            print("ERROR: Homepage returned error")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
