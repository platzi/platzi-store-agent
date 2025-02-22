from langsmith import Client, wrappers
import json
from pipeline import initialize_messages, tools
import openai
from dotenv import load_dotenv
import os
from uuid import uuid4
from langsmith.run_trees import RunTree
from agent_tools import buscar_productos, verificar_descuento

# Cargar variables de entorno
load_dotenv()

# Configurar el cliente de LangSmith
langsmith_client = Client()

# Configurar el cliente de OpenAI con LangSmith
openai_client = wrappers.wrap_openai(openai.Client(api_key=os.getenv("OPENAI_API_KEY")))

# Dataset de pruebas
examples = [
    # Consultas de productos individuales
    {
        "question": "¿Tienen iPhone 14?",
        "expected_response": "El iPhone 14 está disponible a $799. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento"]
    },
    {
        "question": "¿Tienen Samsung Galaxy S23?",
        "expected_response": "¡Sí! El Samsung Galaxy S23 está a $699 y tiene un 10% de descuento. Su precio final es $629.10.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento"]
    },
    {
        "question": "Busco AirPods Pro 2",
        "expected_response": "¡Encontré los AirPods Pro 2! Están a $249 y tienen un 10% de descuento. El precio final es $224.10.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento"]
    },
    {
        "question": "¿Tienen MacBook Air M2?",
        "expected_response": "Sí, tenemos la MacBook Air M2 a $1199. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento"]
    },
    {
        "question": "¿Tienen iPad Pro M2?",
        "expected_response": "¡Sí! El iPad Pro M2 está a $999 y tiene un 20% de descuento. Su precio final es $799.20.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento"]
    },
    # Consultas de múltiples productos
    {
        "question": "¿Qué tienen de Apple, iPhone y MacBook?",
        "expected_response": "Aquí tienes los productos de Apple que buscas:\n\n1. iPhone 14 a $799. No tiene descuentos en este momento.\n2. MacBook Air M2 a $1199. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento", "buscar_productos", "verificar_descuento"]
    },
    {
        "question": "Busco AirPods Pro 2 o Sony WH-1000XM5",
        "expected_response": "¡Encontré lo que buscas! 😊\n\n1. AirPods Pro 2 a $249. ¡Tienen un 10% de descuento! Su precio final es $224.10.\n2. Sony WH-1000XM5 a $349. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento", "buscar_productos", "verificar_descuento"]
    },
    {
        "question": "Me interesan el Samsung Galaxy S23 y el iPhone 14",
        "expected_response": "¡Buenas noticias! 🎉\n\n1. Samsung Galaxy S23 a $699. ¡Tiene un 10% de descuento! Su precio final es $629.10.\n2. iPhone 14 está disponible a $799. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento", "buscar_productos", "verificar_descuento"]
    },
    {
        "question": "¿Tienen Google Pixel 7 Pro o Samsung Galaxy Z Fold 4?",
        "expected_response": "¡Sí! Aquí tienes la información:\n\n1. Google Pixel 7 Pro a $899. ¡Tiene un 10% de descuento! Su precio final es $809.10.\n2. Samsung Galaxy Z Fold 4 a $1799. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento", "buscar_productos", "verificar_descuento"]
    },
    {
        "question": "Muéstrame el Dell XPS 13 Plus y el MacBook Air M2",
        "expected_response": "¡Claro! Aquí tienes la información:\n\n1. Dell XPS 13 Plus a $1399. ¡Tiene un 10% de descuento! Su precio final es $1259.10.\n2. MacBook Air M2 a $1199. No tiene descuentos en este momento.",
        "expected_trajectory": ["buscar_productos", "verificar_descuento", "buscar_productos", "verificar_descuento"]
    }
]

# Nombre del dataset a evaluar
dataset_name = "Platzi Store: Trajectory Evaluation"

try:
    # Crear un nuevo dataset en LangSmith
    dataset = langsmith_client.create_dataset(dataset_name=dataset_name)
except:
    # Si el dataset ya existe, obtener el dataset existente
    datasets = langsmith_client.list_datasets()
    dataset = next(d for d in datasets if d.name == dataset_name)

# Eliminar ejemplos existentes en el dataset
existing_examples = langsmith_client.list_examples(dataset_id=dataset.id)
for example in existing_examples:
    langsmith_client.delete_example(example.id)

# Crear ejemplos en el dataset
langsmith_client.create_examples(
    inputs=[{"question": ex["question"]} for ex in examples],
    outputs=[{
        "response": ex["expected_response"],
        "trajectory": ex["expected_trajectory"]
    } for ex in examples],
    dataset_id=dataset.id
)

# Evaluador de trayectoria que verifica si la trayectoria del agente coincide con la trayectoria esperada.
def trajectory_subsequence(outputs: dict, reference_outputs: dict) -> float:
    expected_pairs = len(reference_outputs["trajectory"]) // 2

    agent_searches = outputs["trajectory"].count("buscar_productos")
    agent_verifications = outputs["trajectory"].count("verificar_descuento")

    complete_pairs = min(agent_searches, agent_verifications)

    score = complete_pairs / expected_pairs

    return score


# Función que ejecuta el agente y registra la trayectoria junto con la respuesta final.
def run_agent_with_tracking(inputs: dict) -> dict:
    """Ejecuta el agente y registra la trayectoria junto con la respuesta final."""
    trajectory = []
    messages = initialize_messages()  # Usar el mismo sistema de mensajes que pipeline.py
    messages.append({"role": "user", "content": inputs["question"]})
    final_response = ""
    
    # Crear el árbol de ejecución para esta evaluación
    evaluation_trace = RunTree(
        name=f"Evaluation: {inputs['question'][:40]}",
        run_type="chain",
        inputs={"question": inputs['question']},
        id=str(uuid4())
    )
    evaluation_trace.post()
    
    try:
        # Ejecutar el agente
        while True:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools  # Usar las mismas herramientas que pipeline.py
            )
            
            assistant_message = response.choices[0].message
            
            # Si hay una respuesta final del agente
            if assistant_message.content:
                final_response = assistant_message.content
                messages.append({"role": "assistant", "content": final_response})
                break
                
            # Si el agente quiere usar funciones
            if assistant_message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": assistant_message.tool_calls
                })
                
                # Procesar cada llamada a función
                for tool_call in assistant_message.tool_calls:
                    if tool_call.type == "function":
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Registrar la función llamada en la trayectoria
                        trajectory.append(function_name)
                        
                        # Ejecutar la función correspondiente
                        if function_name == "buscar_productos":
                            result = buscar_productos(
                                search_term=function_args["search_term"]
                            )
                        elif function_name == "verificar_descuento":
                            result = verificar_descuento(
                                product_id=function_args["product_id"]
                            )
                        
                        # Agregar el resultado a los mensajes
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })
                        
        # Finalizar el árbol de ejecución
        evaluation_trace.end(
            outputs={
                "final_response": final_response,
                "trajectory": trajectory
            }
        )
        evaluation_trace.patch()
        
        # Devolver la respuesta final y la trayectoria
        return {
            "response": final_response,
            "trajectory": trajectory
        }
        
    # En caso de error, registrar la excepción en el árbol de ejecución
    except Exception as e:
        evaluation_trace.end(error=str(e))
        evaluation_trace.patch()
        raise e


# Ejecutar la evaluación del agente como experimento
experiment = langsmith_client.evaluate(
    run_agent_with_tracking,
    data=dataset_name,
    evaluators=[trajectory_subsequence],
    experiment_prefix="platzi-store-trajectory",
    num_repetitions=1,
    max_concurrency=4
)
