import json
from agent_tools import (
    calcular_precio,
    buscar_productos,
    sumar_precios,
    verificar_descuento
)

# Variables globales para el estado de la conversación
messages = []

# Definir las herramientas disponibles para el agente
tools = [
    {
        "type": "function",
        "function": {
            "name": "calcular_precio",
            "description": "Calcula el precio total de un producto según su ID y cantidad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "cantidad": {"type": "integer"}
                },
                "required": ["product_id", "cantidad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_productos",
            "description": "Busca productos que coincidan con un término de búsqueda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {"type": "string"}
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sumar_precios",
            "description": "Calcula la suma total de una lista de precios.",
            "parameters": {
                "type": "object",
                "properties": {
                    "precios": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "required": ["precios"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_descuento",
            "description": "Verifica si un producto tiene descuento y muestra el precio con descuento aplicado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        }
    }
]

def print_function_info(function_name: str, args: dict, result: str = None):
    """
    Función auxiliar para imprimir información de las llamadas a funciones con emojis.
    """
    function_styles = {
        "calcular_precio": {
            "emoji": "🧮",
            "call_format": lambda a: f"Calculando precio (ID: {a['product_id']}, Cantidad: {a['cantidad']})"
        },
        "buscar_productos": {
            "emoji": "🔍",
            "call_format": lambda a: f"Buscando productos con término: '{a['search_term']}'"
        },
        "sumar_precios": {
            "emoji": "🧮",
            "call_format": lambda a: f"Sumando precios: {', '.join([f'${p:.2f}' for p in a['precios']])}"
        },
        "verificar_descuento": {
            "emoji": "🏷️",
            "call_format": lambda a: f"Verificando descuento para producto ID: {a['product_id']}"
        }
    }
    
    style = function_styles.get(function_name, {})
    if style:
        print(f"\n{style['emoji']} {style['call_format'](args)}")
    if result:
        print(f"➡️ {result}")

def initialize_messages():
    """
    Inicializa el sistema con instrucciones y listado de productos.
    """
    
    system_content = f"""
Eres un agente virtual llamado **Platzi Store Agent**, especializado en ayudar a los usuarios a encontrar productos electrónicos de manera eficiente y personalizada.

Tu objetivo es ofrecer información útil, personalizada y alineada con las necesidades del usuario, destacando siempre los descuentos disponibles.
"""
    return [{"role": "system", "content": system_content.strip()}]

def run_agent(client, user_input):
    """
    Función principal que gestiona la conversación con el agente.
    """
    global messages
    
    # Si es la primera vez, inicializa los mensajes del sistema
    if not messages:
        messages = initialize_messages()
    
    # Agrega el mensaje del usuario
    messages.append({"role": "user", "content": user_input})

    try:
        # Iteraremos hasta que el agente produzca una respuesta final en texto
        while True:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )

            assistant_message = response.choices[0].message

            # Si hay una respuesta textual final del agente, imprímela y guárdala
            if assistant_message.content:
                print(f"\n🤖 Agente: {assistant_message.content}")
                messages.append({"role": "assistant", "content": assistant_message.content})

            # Verifica si el agente está solicitando ejecutar alguna función
            if not assistant_message.tool_calls:
                break

            # Agrega el mensaje del agente con llamadas a funciones a la conversación
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": assistant_message.tool_calls
            })

            # Ejecuta cada llamada a función
            for tool_call in assistant_message.tool_calls:
                if tool_call.type == "function":
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Elige y ejecuta la función
                    if function_name == "calcular_precio":
                        result = calcular_precio(
                            product_id=function_args["product_id"],
                            cantidad=function_args["cantidad"]
                        )
                    elif function_name == "buscar_productos":
                        result = buscar_productos(
                            search_term=function_args["search_term"]
                        )
                    elif function_name == "sumar_precios":
                        result = sumar_precios(
                            precios=function_args["precios"]
                        )
                    elif function_name == "verificar_descuento":
                        result = verificar_descuento(
                            product_id=function_args["product_id"]
                        )

                    print_function_info(function_name, function_args, result)

                    # Registra la salida de la función en la conversación
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

    except Exception as e:
        raise e

    print()
