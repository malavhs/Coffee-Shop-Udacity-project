from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
def get_drinks():
    list_of_drinks = Drink.query.all()
    shorted_drinks = []

    for i in list_of_drinks:
        shorted_drinks.append(i.short())
    
    return jsonify({
        'success': 'True',
        'drinks': shorted_drinks
    }), 200



'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_detailed_drinks_list(payload):
    list_of_drinks = Drink.query.all()
    long_drinks = []

    for i in list_of_drinks:
        long_drinks.append(i.long())
    
    return jsonify({
        'success': 'True',
        'drinks': long_drinks
    }), 200

'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drinks(payload):
    body = request.get_json()
    if not body:
        abort(404)
    recipe_name = json.dumps(body.get('recipe'))
    title_name = body.get('title')
    if recipe_name is None or title_name is None:
        abort(400)
    new_drink = Drink(title = title_name, recipe = recipe_name)
    new_drink.insert()
    final_long_drink = new_drink.long()
    return jsonify({
        'success': 'True',
        'drinks': final_long_drink
    }), 200


    


'''
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def change_drink(payload, drink_id):
    # Specify match condition
    match_condition = Drink.id == drink_id
    # Filter drink needed
    interested_drink = Drink.query.filter(match_condition).one_or_none()
    if interested_drink is None:
        abort(404)
    # Get Body details
    body = request.get_json()
    interested_drink.recipe = json.dumps(body.get('recipe'))
    interested_drink.title = body.get('title')
    interested_drink.update()
    final_long_drink = interested_drink.long()

    return jsonify({
        'success': 'True',
        'drinks': [final_long_drink]
    }), 200

'''
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_from_list(payload, drink_id):
    # Specify match condition
    match_condition = Drink.id == drink_id
    # Filter drink needed
    interested_drink = Drink.query.filter(match_condition).one_or_none()
    if interested_drink is None:
        abort(404)
    interested_drink.delete()

    return jsonify({
        'success': 'True',
        'delete': drink_id
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resource_not_fond(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500

@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not allowed to access this"
    }), 401

@app.errorhandler(400)
def request_bad(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "This is a bad request"
    }), 400

@app.errorhandler(403)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Request forbidden"
    }), 403

'''
implement error handler for 404
    error handler should conform to general task above
'''


'''
implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_err(error):
    stat_cd = error.status_code
    error_msg = error.error['description']
    return jsonify({
        "success": False,
        "error": stat_cd,
        "message": error_msg
    }),stat_cd
    