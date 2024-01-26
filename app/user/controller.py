from flask import request  

def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['birthdate']
    print(name, email, password, dob)
    return "User Registered", 200