from openai import OpenAI
from langsmith import Client
from pipeline import initialize_messages, tools
from agent_tools import (
    calcular_precio,
    buscar_productos,
    sumar_precios,
    verificar_descuento
)
from dotenv import load_dotenv
import json

load_dotenv()

openai_client = OpenAI()
client = Client()

# Función objetivo que simula el comportamiento del agente en la vida real.
def target(inputs: dict) -> dict:
    try:
        print("\n=== TARGET FUNCTION ===")
        print(f"Input recibido: {inputs}")
        print(f"Tipo de input: {type(inputs)}")
        
        messages = initialize_messages()
        print(f"Mensajes iniciales: {messages}")
        
        question = inputs.get("question", "") if isinstance(inputs, dict) else inputs
        print(f"Pregunta procesada: {question}")
        
        messages.append({"role": "user", "content": question})
        print(f"Mensajes finales: {messages}")
        
        while True:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools
                )
                
                assistant_message = response.choices[0].message
                
                if assistant_message.content:
                    result = {"output": assistant_message.content}
                    print(f"Respuesta del agente: {result}")
                    return result
                
                if assistant_message.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": assistant_message.tool_calls
                    })
                    
                    for tool_call in assistant_message.tool_calls:
                        try:
                            if tool_call.type == "function":
                                function_name = tool_call.function.name
                                function_args = json.loads(tool_call.function.arguments)
                                
                                # Ejecutar la función correspondiente
                                if function_name == "calcular_precio":
                                    result = calcular_precio(**function_args)
                                elif function_name == "buscar_productos":
                                    result = buscar_productos(**function_args)
                                elif function_name == "sumar_precios":
                                    result = sumar_precios(**function_args)
                                elif function_name == "verificar_descuento":
                                    result = verificar_descuento(**function_args)
                                else:
                                    result = f"Función {function_name} no implementada"
                                
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": result
                                })
                                
                                print(f"Procesada llamada a función: {function_name}")
                                print(f"Resultado: {result}")
                        except Exception as e:
                            print(f"Error procesando función {function_name}: {str(e)}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Error: {str(e)}"
                            })
                
            except Exception as e:
                print(f"Error en llamada a OpenAI: {str(e)}")
                return {"output": f"Error: {str(e)}"}
                
    except Exception as e:
        print(f"Error en target: {str(e)}")
        return {"output": f"Error procesando la solicitud: {str(e)}"}


# Evaluador de amabilidad donde se evalúa si el agente fue amable al responder en la vida real.
def kindness(outputs: dict, reference_outputs: dict) -> dict:
    question = reference_outputs.get("question", "") if isinstance(reference_outputs, dict) else reference_outputs
    expected = reference_outputs.get("answer", "") if isinstance(reference_outputs, dict) else reference_outputs
    response_text = outputs.get("output", "") if isinstance(outputs, dict) else outputs

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                Evaluar la respuesta del agente:

                ¿El agente fue amable al responder en la vida real? Independientemente de si encontró o no el producto, o del costo del producto.

                - True: Si fue amable
                - False: No fue amable

                Algunos factores que puedes tomar en cuenta y no son excluyentes son: efusividad, voluntad de ayudar y de presentar el producto con buenas referencias
                """
            },
            {
                "role": "user",
                "content": f"""
                    Pregunta del cliente fue: {question}
                    La respuesta de referencia esperada fue: {expected}
                    La respuesta real del agente fue: {response_text}
                """
            }
        ],
    )

    result = {
        "key": "kindness",
        "score": response.choices[0].message.content.strip().lower() == "true"
    }

    return result


# Evaluador de emojis donde se evalúa si el agente coloca emojis en su respuesta.
def contains_emoji(outputs: dict, reference_outputs: dict) -> dict:
    common_emojis = [
        "😊", "❤️", "👍", "😂", "🙌", "✨", "🎉", "🔥", "💪", "👏",
        "🌟", "💯", "🤔", "👀", "💜", "✅", "🎈", "🌈", "🙏", "⭐",
        "💻", "📱", "🖥️", "⌨️", "🖱️", "💾", "📦", "🛒", "🛍️", "🔋",
        "🧑‍💻", "📡", "📊", "📈", "🖋️", "🖇️", "🏷️", "💳", "💡", "🔧"
    ]
    response_text = outputs.get("output", "")
    has_emoji = any(emoji in response_text for emoji in common_emojis)
    result = {
        "key": "contains_emoji",
        "score": has_emoji
    }
    return result


# Nombre del dataset a evaluar
dataset_name = "Platzi Store Dataset v2"

# Ejecuta la evaluación del agente
experiment = client.evaluate(
    target,
    data=dataset_name,
    evaluators=[kindness, contains_emoji],
    experiment_prefix="platzi-store-eval",
    description="Mide la amabilidad del agente y si coloca emojis en su respuesta",
    max_concurrency=1
)
