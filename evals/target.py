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

openai_client = OpenAI()

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
