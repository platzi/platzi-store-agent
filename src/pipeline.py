import json
from agent_tools import (
    calcular_precio,
    buscar_productos,
    sumar_precios,
    verificar_descuento
)
from langsmith.run_trees import RunTree
from uuid import uuid4

# Variables globales para el estado de la conversación
messages = []
conversation_trace = None

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


## Reglas
- Siempre debes responder con emojis
- No preguntes al usuario, salvo el usuario te pida ayuda para elegir, por el contrario ofrece productos inmediatamente
- Si el producto tiene un costo alto (>$1000), ofrece un descuento llamando a la función verificar_descuento
- Siempre debes responder con amabilidad:

## Comportamiento del agente

En este caso ofreció descuentos:

Input: ¿Cuál es la mejor opción para streaming?
Output: El Roku Streaming Stick 4K+ es perfecto para streaming. 🎥 Cuesta $69 y ofrece resolución 4K con control remoto por voz. ¿Quieres que revise si hay descuentos? 😉

En este caso no fue muy breve

Input: ¿Hay descuentos para el PlayStation 5?
Output Negativo (lo que debes evitar):  ¡Buenas noticias! 🎉 El **PlayStation 5** tiene un **10% de descuento**., - **Precio original:** $499.00, - **Descuento:** $49.90, - **Precio final:** $449.10 💰
Output Positivo (lo que debes apuntar): El PlayStation 5 está a $499. 🎮 Ahora mismo verifico si hay algún descuento o promoción disponible.
"""
    return [{"role": "system", "content": system_content.strip()}]

def run_agent(client, user_input):
    """
    Función principal que gestiona la conversación con el agente.
    """
    global messages, conversation_trace
    
    # Si es la primera vez, inicializa los mensajes del sistema
    if not messages:
        messages = initialize_messages()

        conversation_trace = RunTree(
            name="Platzi Store Conversation",
            run_type="chain",
            inputs={"initial_messages": messages},
            id=str(uuid4())
        )
        conversation_trace.post()
    
    # Agrega el mensaje del usuario
    messages.append({"role": "user", "content": user_input})

    interaction_run = conversation_trace.create_child(
        name=f"User Interaction: {user_input[:40]}",
        run_type="chain",
        run_id=str(uuid4())
    )
    interaction_run.post()

    try:
        # Iteraremos hasta que el agente produzca una respuesta final en texto
        while True:

            llm_run = interaction_run.create_child(
                name="Agent Call",
                run_type="llm",
                run_id=str(uuid4())
            )
            llm_run.post()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                langsmith_extra={"run_tree": llm_run}
            )

            llm_run.end(outputs={"response": response.model_dump()})
            llm_run.patch()

            assistant_message = response.choices[0].message

            # Si hay una respuesta textual final del agente, imprímela y guárdala
            if assistant_message.content:
                print(f"\n🤖 Agente: {assistant_message.content}")
                messages.append({"role": "assistant", "content": assistant_message.content})

            # Verifica si el agente está solicitando ejecutar alguna función
            if not assistant_message.tool_calls:
                break

            tool_call_run = interaction_run.create_child(
                name="Function Calls Processing",
                run_type="chain",
                run_id=str(uuid4())
            )
            tool_call_run.post()

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

                    # Elige y ejecuta la función, registrando su actividad en el árbol
                    if function_name == "calcular_precio":
                        func_run = tool_call_run.create_child(
                            name="Calculate Price Function",
                            run_type="tool",
                            run_id=str(uuid4())
                        )
                        func_run.post()
                        result = calcular_precio(
                            product_id=function_args["product_id"],
                            cantidad=function_args["cantidad"],
                            langsmith_extra={"run_tree": func_run}
                        )
                        print_function_info(function_name, function_args, result)
                        func_run.end(outputs={"result":result})
                        func_run.patch()
                    elif function_name == "buscar_productos":
                        func_run = tool_call_run.create_child(
                            name="Search Products Function",
                            run_type="tool",
                            run_id=str(uuid4())
                        )
                        func_run.post()
                        result = buscar_productos(
                            search_term=function_args["search_term"],
                            langsmith_extra={"run_tree": func_run}
                        )
                        print_function_info(function_name, function_args, result)
                        func_run.end(outputs={"result": result})
                        func_run.patch()

                    elif function_name == "sumar_precios":
                        func_run = tool_call_run.create_child(
                            name="Sum Prices Function",
                            run_type="tool",
                            run_id=str(uuid4())
                        )
                        func_run.post()
                        result = sumar_precios(
                            precios=function_args["precios"],
                            langsmith_extra={"run_tree": func_run}
                        )
                        print_function_info(function_name, function_args, result)
                        func_run.end(outputs={"result": result})
                        func_run.patch()

                    elif function_name == "verificar_descuento":
                        func_run = tool_call_run.create_child(
                            name="Check Discount Function",
                            run_type="tool",
                            run_id=str(uuid4())
                        )
                        func_run.post()
                        result = verificar_descuento(
                            product_id=function_args["product_id"],
                            langsmith_extra={"run_tree": func_run}
                        )
                        print_function_info(function_name, function_args, result)
                        func_run.end(outputs={"result": result})
                        func_run.patch()

                    # Registra la salida de la función en la conversación
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            
            tool_call_run.end(outputs={"messages": messages})
            tool_call_run.patch()
            # El bucle continúa => el agente ve mensajes actualizados (salidas de funciones) y
            # puede decidir llamar a más funciones o finalizar.
        
        interaction_run.end(
            outputs={
                "final_messages": messages,
                "status": "completed"
            }
        )
        interaction_run.patch()

        # Actualiza el árbol de ejecución principal para la siguiente consulta
        conversation_trace.end(
            outputs={
                "current_messages": messages,
                "status": "in_progress"
            }
        )
        conversation_trace.patch()

    except Exception as e:
        # En caso de error, registra la excepción en el árbol de ejecución
        interaction_run.end(
            error=str(e),
            outputs={
                "final_messages": messages,
                "status": "in_progress"
            }
        )
        interaction_run.patch()
        raise e

    print()
