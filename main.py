from google import genai
from pydantic import BaseModel 
from rapidfuzz import process, fuzz
import json

number_people=7#input("# of people")
ingredients="basmatti rice, 3 chicken breast, indian spices, 5 tomatoes, 1 red onion, 1 whole garlic, 1 ginger "#input("ingredients with amounts")

class Dish(BaseModel):
    dish_name: str
    valid_ingreients: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"i need suggestions for dishes for this many people: {number_people}, i have these indredients with their ammounts: {ingredients}, show ammounts as well,assume user has basic spices or also include alternative spices where possible, show me at leaste more than 3 dishes but less than 10",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Dish],
    },
)

# Use the response as a JSON string.
print(response.text)
data=json.loads(response.text)

dish=input("From list choose dish")

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
    print("Ingredients:")
    for item in ingredients:
        print(f" - {item}")

    
print(dish_name, ingredients)

class Recipe(BaseModel):
    dish: str
    recipe: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Ive choosen {dish} for {number_people} people, with only these {ingredients}, please give the enitre recipe",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Recipe],
    },
)
# Use the response as a JSON string.
print(response.text)

