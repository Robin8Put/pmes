import requests
from tornado_components import mongo
from tornado_components.timestamp import get_time_stamp

table = mongo.Table(dbname="pmes", collection="accounts")
#table.collection.remove()

# Create new account with public key, signature and message
valid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=valid_data)
assert isinstance(request.json(), dict)
assert "public_key" in request.json().keys()
assert "id" in request.json().keys()
assert "count" in request.json().keys()
assert "level" in request.json().keys()
assert "email" in request.json().keys()
assert "device_id" in request.json().keys()
assert "href" in request.json().keys()
assert "balance" in request.json().keys()

# Try to repeat creating
valid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=valid_data)
print(request.text)

# Create new account with invalid signature
valid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eaef217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=valid_data)
assert request.status_code == 403



# Create new account without public key
invalid_data1 = {
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=invalid_data1)
assert request.status_code == 403




# Create new account without signature
invalid_data1 = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=invalid_data1)
assert request.status_code == 403

# Create new account without message
invalid_data1 = {
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=invalid_data1)
assert request.status_code == 403

# Create new account with public key, signature, message
#			and without all required fields
invalid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:8000/api/accounts", data=invalid_data)
assert request.status_code == 400

# Get balance
request = requests.get("http://127.0.0.1:8000/api/accounts/04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa/balance")
print(request.json())


# Get accounts data
request = requests.get("http://127.0.0.1:8000/api/accounts/04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa")
print(request.json())



table.collection.remove()