from flask import Flask, render_template, request
from google import genai
from pydantic import BaseModel 
from rapidfuzz import process, fuzz
import json

app = Flask(__name__, template_folder='html', static_folder='static', static_url_path='/')

mylist = "" 
mods = ""
number = ""
response = ""
recipe = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global mylist, mods, number, response, recipe
    if request.method == 'GET':
        return render_template('index.html', mylist=mylist, mods=mods, number=number, response=response, recipe=recipe)

    else:
            
            # Check if form is empty (might indicate a different issue)

        if 'button_ingredient' in request.form:
            if request.form['ingredients']:
                mylist=[request.form['ingredients']]
            else:
                mylist = ""

        elif 'button_mods' in request.form:
            if request.form['mod']:
                mods=[request.form['mod']]
            else:
                mods = ""
            
        elif 'button_number' in request.form:
            if request.form['number_people']:
                number = request.form['number_people']
            else:
                number = ""

        elif 'button_generate' in request.form:
            if mylist != "" and number != "":
                response = get_dishes(number, mylist, mods)

        elif 'this_dish' in request.form:
            recipe = pick_dish(request.form['this_dish'],response,number)

        return render_template('index.html', mylist=mylist, mods=mods, response=response, number=number, recipe=recipe)


def get_dishes(number_people, ingredients, modifers):

    if modifers!="":    
        prompt=f"""I need suggestions for dishes for this many people: {number_people}, 
        I have these indredients with their ammounts: {ingredients},
        I have these requirments of the dish as well: {modifers},
        show ammounts as well if not amounts were given for ingredients then create ammounts based on the amount of people, 
        assume user has basic spices or also include alternative spices where possible, 
        show me 4 dishes"""
    else:
        prompt=f"""i need suggestions for dishes for this many people: {number_people}, 
        i have these indredients with their ammounts: {ingredients}, 
        show ammounts as well if not amounts were given for ingredients then create ammounts based on the amount of people, 
        assume user has basic spices or also include alternative spices where possible, 
        show me 4 dishes"""

    class Dish(BaseModel):
        dish_name: str
        valid_ingredients: list[str]

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Dish],
        },
    )

    # Use the response as a JSON string.
    data=json.loads(response.text)
    return data

def pick_dish(dish_picked,response,number):##dish picked is an int 0 in top left 3 in bottom right
    dish_name = "Unknown dish"
    ingredients = []

    if response != "":
        selected = response[int(dish_picked)]
        dish_name = selected["dish_name"]
        ingredients = selected["valid_ingredients"]

    class Recipe(BaseModel):
        dish: str
        recipe: list[str]
        valid_ingredients: list[str]

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"""Ive choosen {dish_name} for {number} people, with only these {ingredients}, 
        if there are extra ingredients that the user does not state to have then do not try to use them only stick to ingredients they have entered or state them as extra needed ingredients, 
        give the enitre recipe""",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Recipe],
        },
    )
    # Use the response as a JSON string.
    print(response.text)
    data=json.loads(response.text)
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
