import os
import openai
from dotenv import load_dotenv
from pipeline import run_agent

def main():
    """
    Función principal que inicializa y ejecuta el agente de Platzi Store.
    """
    # Cargar variables de entorno necesarias para el agente
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Falta la variable de entorno OPENAI_API_KEY.")
    
    # Configurar el cliente de OpenAI
    client = openai.Client(api_key=openai_api_key)
    
    print("\n🏪 Bienvenido a Platzi Store! 🛍️")
    print("Escribe 'salir' en cualquier momento para terminar la conversación.\n")

    while True:
        try:
            user_input = input("👤 Tú: ")
            if user_input.lower() == "salir":
                print("\n👋 ¡Gracias por usar Platzi Store! ¡Hasta pronto!")
                break

            # Ejecutar el agente
            run_agent(client, user_input)

        except KeyboardInterrupt:
            print("\n👋 ¡Gracias por usar Platzi Store! ¡Hasta pronto!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            break

if __name__ == "__main__":
    main()
