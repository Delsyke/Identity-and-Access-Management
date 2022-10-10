import os
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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.get('/drinks')
def get_drinks():
    drink_query = Drink.query.all()

    if len(drink_query) != 0:
        drinks = [drink.short() for drink in drink_query]
        return jsonify({
            "success" : True,
            "drinks" : drinks
            }), 200
    else:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.get('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(jwt):
    drink_query = Drink.query.all()

    if len(drink_query) != 0:
        drinks_detail = [drink.long() for drink in drink_query]
        return jsonify({
            "success" : True,
            "drinks" : drinks_detail
            }), 200
    else:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.post('/drinks')
@requires_auth(permission='post:drinks')
def post_drinks(jwt):

    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()

    return jsonify({
        "success" : True,
        "drinks" : drink.long()
        }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.patch('/drinks/<int:id>')
@requires_auth(permission='patch:drinks')
def patch_drink(jwt, id=id):
    # request body
    body = request.get_json() 
    new_title = body.get('title')
    new_recipe = body.get('recipe')
        
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)
    else:
        if new_title:
            drink.title = new_title

        if new_recipe:
            drink.recipe = json.dumps(new_recipe)

        drink.update()
        return jsonify({
            "success":True,
            "drinks" : [drink.long()]
            }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.delete('/drinks/<int:id>')
@requires_auth(permission='delete:drinks')
def delete_drink(jwt, id=id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink:
        drink.delete()
        return jsonify ({
            "success" : True,
            "delete" : id
            }), 200
    else:
        abort(404)

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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def not_authenticated(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not authenticated"
    }), 401


@app.errorhandler(403)
def not_authorised(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "not authorised"
    }), 403


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({
        "success":False,
        "error": error.status_code,
        "message": error.error,
        }), error.status_code


if __name__ == "__main__":
    app.debug = True
    app.run()


