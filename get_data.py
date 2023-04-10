import requests
from requests.auth import HTTPBasicAuth

import json
import komoot
import os

login_url = "https://account.komoot.com/v1/signin"

email_global = ""
password_global = ""

s = requests.Session()
cookies = {}

def auth(email, password) -> bool:
	global email_global
	global password_global

	email_global = email

	if password == "!file":
		with open("pwd.txt", "r") as f:
			password = f.read().strip()

	password_global = password

	res = requests.get(login_url)
	cookies = res.cookies.get_dict()


	headers = {
		"Content-Type": "application/json"
	}

	payload = json.dumps({
		"email": email_global,
		"password": password_global,
		"reason": "null"
	})

	r = s.post(login_url,
		headers=headers,
		data=payload,
		cookies=cookies,
	)

	url = "https://account.komoot.com/actions/transfer?type=signin"
	s.get(url)

	return json.loads(r.text)["type"] == "logged_in"

def check_auth(client_id):
	url = f"https://api.komoot.de/v007/users/{client_id}/tours/"

	response = s.get(url, auth=HTTPBasicAuth(email_global, password_global))
	return response.status_code == 200

def get_tours(client_id, recorded=True, planned=False):
	url = f"https://api.komoot.de/v007/users/{client_id}/tours/"

	response = s.get(url, auth=HTTPBasicAuth(email_global, password_global))
	if response.status_code != 200:
		print("Something went wrong...")
		print(response.text)
		print(response.status_code)
		
		return False

	data = response.json()

	tours = data["_embedded"]["tours"]

	# Filter tours
	return_tours = []
	for tour in tours:
		if tour['type'] == "tour_recorded" and recorded:
			return_tours.append(tour)
		elif tour['type'] == "tour_planned" and planned:
			return_tours.append(tour)

	return return_tours

def get_tour_gpx(tour_id):
	url = f"https://www.komoot.de/api/v007/tours/{tour_id}.gpx?hl=de"

	response = s.get(url, cookies=cookies)
	if response.status_code != 200:
		print("Something went wrong...")
		print(response.text)
		print(response.status_code)
		exit(1)

	data = response.text

	return data


if __name__ == "__main__":
	auth("05262020@protonmail.com", "!file")
	tours = get_tours(3036801734530)

	for i, tour in enumerate(tours):
		print(f"{i}: {tour['name']} - {tour['id']}")
	
	print(get_tour_gpx(tours[0]['id']))