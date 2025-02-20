import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
import os
from dotenv import load_dotenv
load_dotenv()

# Auto-trace agente calls in-context
client = wrap_openai(openai.Client(api_key=os.getenv("OPENAI_API_KEY")))

@traceable # Auto-trace this function
def pipeline(user_input: str):
    result = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="gpt-4o-mini"
    )
    return result.choices[0].message.content

print(pipeline("¡Hola! ¿Cómo estás?"))
