from google import genai
import os

client = genai.Client(api_key= os.environ.get("API_Key"))

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Make a spagetti recepi"
)
print(response.text)
