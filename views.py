from flask import Blueprint, render_template

main = Blueprint('main', __name__) #give it name, pass in name of module

#add routes to main object 
@main.route('/')
def index():
    return render_template('home.html')

