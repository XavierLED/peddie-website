from google import genai
from pydantic import BaseModel 
from rapidfuzz import process, fuzz
import json

number_people=input("# of people: ")
ingredients=input("ingredients with amounts: ")
modifers=input("Culinary Style, Nutritional Requirments, Preperation Method, Alergies, Other Modifiers")

if modifers!="":    
    prompt=f"""I need suggestions for dishes for this many people: {number_people}, 
    I have these indredients with their ammounts: {ingredients},
    I have these requirments of the dish as well: {modifers},
    show ammounts as well, assume user has basic spices or also include alternative spices where possible, 
    show me at leaste more than 3 dishes but less than 10"""
else:
    prompt=f"""i need suggestions for dishes for this many people: {number_people}, 
    i have these indredients with their ammounts: {ingredients}, 
    show ammounts as well, assume user has basic spices or also include alternative spices where possible, 
    show me at leaste more than 3 dishes but less than 10"""

class Dish(BaseModel):
    dish_name: str
    valid_ingreients: list[str]

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
print(response.text)

data=json.loads(response.text)

valid_dish=False
while valid_dish==False:
    dish=input("From list choose dish: ")

    choices = [d["dish_name"] for d in data]
    best_match, score, idx = process.extractOne(
        dish, choices, scorer=fuzz.WRatio
    )

    if score < 60:  # threshold, tweak as needed
        print("Couldn't find a close enough match. Try again.")
    else:
        selected = data[idx]
        dish_name = selected["dish_name"]
        ingredients = selected["valid_ingreients"]

        print(f"\nYou picked: {dish_name} (match score: {score})")
        print("ingredients:")
        for item in ingredients:
            print(f" - {item}")
        valid_dish=True

    
print(dish_name, ingredients)

class Recipe(BaseModel):
    dish: str
    recipe: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=f"""Ive choosen {dish_name} for {number_people} people, with only these {ingredients}, 
    if there are extra ingredients that the user does not state to have then do not try to use them only stick to ingredients they have entered or state them as extra needed ingredients, 
    give the enitre recipe""",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Recipe],
    },
)
# Use the response as a JSON string.
print(response.text)

