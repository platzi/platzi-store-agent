from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client()

# Ejemplos de preguntas y respuestas
examples = [
    ("¿Tienen disponible el iPhone 14?", 
     "¡Claro! 📱 Actualmente tenemos 100 unidades del iPhone 14 en stock. Es el último modelo con funciones avanzadas y una pantalla impresionante. Su precio es de $799. ¿Quieres que te confirme si hay algún descuento disponible? 😊"),
    
    ("¿Cuál es el precio del Samsung Galaxy S23?", 
     "El Samsung Galaxy S23 está a $699. 🤩 Es un smartphone increíble con un procesador potente y cámara profesional. Ahora verifico si tiene algún descuento para ti. 🛒✨"),
    
    ("¿Qué tan bueno es el MacBook Air M2?", 
     "El MacBook Air M2 es excelente. 💻 Su chip M2 lo hace súper rápido y eficiente, y su pantalla Retina es espectacular para cualquier tarea. Cuesta $1199 y tenemos 50 unidades disponibles. ¿Te interesa que revise si tiene un descuento especial? 😉"),
    
    ("¿Cuántos AirPods Pro 2 tienen disponibles?", 
     "Actualmente tenemos 200 unidades de los AirPods Pro 2. 🎧✨ Son auriculares premium con cancelación activa de ruido y audio espacial. Su precio es de $249. ¿Te gustaría que revise promociones activas? 🛒"),
    
    ("¿Hay descuentos para el PlayStation 5?", 
     "El PlayStation 5 está a $499. 🎮 Ahora mismo verifico si hay algún descuento o promoción disponible. 🚀 Un momento, por favor."),
    
    ("¿Qué ventajas tiene el Google Pixel 7 Pro?", 
     "El Google Pixel 7 Pro destaca por su cámara increíble y funciones avanzadas de inteligencia artificial. 📸✨ Su precio actual es de $899 y tenemos 80 unidades disponibles. ¿Deseas que revise descuentos o facilidades de pago? 😊"),
    
    ("¿Me puedes ayudar con un teclado compacto?", 
     "¡Por supuesto! 🎹 Te recomiendo el Logitech MX Keys Mini, que cuesta $99. Es un teclado compacto, con teclas retroiluminadas y conexión Bluetooth. Ahora verifico si tiene alguna promoción activa. 💡"),
    
    ("¿Cuál es la mejor cámara para grabar contenido?", 
     "La Sony ZV-E10 es ideal para creadores de contenido. 🎥 Tiene calidad de video 4K y cuesta $899. ¿Te gustaría que revise su disponibilidad y descuentos? 🤔"),
    
    ("¿El Fitbit Versa 4 es resistente al agua?", 
     "Sí, el Fitbit Versa 4 es resistente al agua. 🌊 Además, tiene seguimiento avanzado de salud y fitness. Su precio es de $229. ¿Reviso si hay alguna oferta para este producto? 😊"),
    
    ("¿Tienen drones disponibles?", 
     "¡Claro que sí! 🚁 Tenemos el DJI Mavic 3 Classic por $1599. Es un dron profesional con cámara Hasselblad y gran alcance. ¿Te interesa que revise promociones o descuentos? 🛒"),
    
    ("¿Puedo comprar el Nintendo Switch OLED hoy mismo?", 
     "Sí, el Nintendo Switch OLED está disponible por $349. 🎮 Tenemos 200 unidades en stock. ¡Puedes comprarlo hoy mismo! ¿Te ayudo a revisar si hay algún descuento? 😊"),
    
    ("¿Qué precio tiene la NVIDIA GeForce RTX 4090?", 
     "La NVIDIA GeForce RTX 4090 cuesta $1599. 💻 Es la tarjeta gráfica más potente para gaming extremo. Actualmente quedan 10 unidades. ¿Reviso si hay alguna oferta especial? 😎"),
    
    ("¿Tienen el iPad Pro M2?", 
     "¡Sí! 📱 El iPad Pro M2 está disponible por $999. Es el iPad más potente con pantalla Liquid Retina XDR. Tenemos 30 unidades en stock. ¿Quieres que revise si hay alguna promoción activa? 🤩"),
    
    ("¿Qué tablet recomiendas para estudiantes?", 
     "Te recomiendo la Samsung Galaxy Tab S8 Ultra. 📝 Tiene una gran pantalla AMOLED y viene con el S Pen incluido. Su precio es de $1099. ¿Te gustaría saber si hay algún descuento? 😊"),
    
    ("¿Cuántas unidades de la Dell XPS 13 Plus tienen?", 
     "Tenemos 40 unidades de la Dell XPS 13 Plus disponibles. 💻 Es un portátil elegante con rendimiento superior. Su precio es de $1399. ¿Quieres que verifique descuentos o promociones? 🔍"),
    
    ("¿Qué producto recomiendas para edición de video?", 
     "Para edición de video, te recomiendo la MacBook Air M2 o la Dell XPS 13 Plus. 🎥 Ambas tienen excelente rendimiento. ¿Reviso cuál tiene mejor descuento actualmente? 😊"),
    
    ("¿Cuál es el costo del Dyson Airwrap?", 
     "El Dyson Airwrap cuesta $599. 💨 Es un kit de estilizado premium para el cabello. Tenemos 50 unidades en stock. ¿Te interesa que revise si tiene alguna promoción activa? 😊"),
    
    ("¿Tienen el Samsung Galaxy Z Fold 4?", 
     "¡Sí! 📱 El Samsung Galaxy Z Fold 4 está disponible por $1799. Es un teléfono plegable con pantalla AMOLED. Tenemos 25 unidades en stock. ¿Reviso si hay descuentos? 🤩"),
    
    ("¿Cuáles son las especificaciones del HyperX Cloud III?", 
     "El HyperX Cloud III tiene sonido envolvente y un diseño súper cómodo. 🎧 Ideal para gaming. Su precio es de $129 y tenemos 120 unidades disponibles. ¿Quieres que revise ofertas especiales? 😎"),
    
    ("¿Hay promociones para auriculares?", 
     "Tenemos varias opciones, como:\n• 🎧 AirPods Pro 2: $249\n• 🎧 Sony WH-1000XM5: $349\n• 🎧 Bose QuietComfort Earbuds II: $299\nAhora mismo reviso si alguna tiene descuento. 😊"),
    
    ("¿Qué recomiendas para jugar videojuegos?", 
     "Para jugar videojuegos, te recomiendo:\n• 🎮 PlayStation 5: $499\n• 🎮 Xbox Series X: $499\n• 🎮 Nintendo Switch OLED: $349\n¿Reviso descuentos para alguno en específico? 😊"),
    
    ("¿Qué laptop tiene mejor pantalla táctil?", 
     "La Microsoft Surface Laptop 5 es una excelente opción. 💻 Tiene pantalla táctil PixelSense y cuesta $1299. Tenemos 25 unidades disponibles. ¿Reviso si tiene alguna promoción? 🤔"),
    
    ("¿Cuáles son los mejores auriculares para trabajar?", 
     "Te recomiendo:\n• 🎧 Sony WH-1000XM5: $349\n• 🎧 Bose QuietComfort Earbuds II: $299\nAmbos son excelentes para eliminar ruido mientras trabajas. 😊 ¿Reviso cuál tiene mejor descuento?"),
    
    ("¿Qué teclado mecánico recomiendas?", 
     "El Corsair K100 RGB es increíble. ⌨️ Tiene iluminación RGB dinámica y controles programables. Cuesta $229 y tenemos 60 unidades disponibles. ¿Quieres que revise si hay promociones? 😊"),
    
    ("¿Tienen cámaras de seguridad disponibles?", 
     "Sí, tenemos la Eufy Security SoloCam S40. 📹 Es una cámara solar con grabación 2K y detección de movimiento. Cuesta $199. ¿Reviso descuentos activos para ti? 😊"),
    
    ("¿Qué tan rápido es el Samsung Portable SSD T9?", 
     "El Samsung Portable SSD T9 es súper rápido y confiable. 💾 Tiene 2TB de capacidad y cuesta $229. Tenemos 70 unidades disponibles. ¿Te interesa que revise si tiene algún descuento? 😊"),
    
    ("¿Cuál es la mejor opción para streaming?", 
     "El Roku Streaming Stick 4K+ es perfecto para streaming. 🎥 Cuesta $69 y ofrece resolución 4K con control remoto por voz. ¿Quieres que revise si hay descuentos? 😉"),
    
    ("¿Tienen laptops gaming?", 
     "Sí, te recomiendo:\n• 🎮 Asus ROG Flow X16: $1999\n• 🎮 Razer Blade 18: $2999\nAmbas tienen especificaciones premium. ¿Te interesa que revise promociones para alguna? 😊"),
    
    ("¿Cuál es el precio del Kindle Scribe?", 
     "El Kindle Scribe está a $339. 📚 Es ideal para leer y escribir. Tenemos 100 unidades en stock. ¿Quieres que revise si tiene alguna promoción activa? 😊"),
    
    ("¿Tienen televisores OLED?", 
     "¡Sí! Tenemos el LG OLED evo C3 por $1799. 📺 Ofrece colores vibrantes y tecnología HDR avanzada. ¿Reviso descuentos para ti? 😉")
]

# Crear ejemplos de entrada y salida
inputs = [{"question": input_prompt} for input_prompt, _ in examples ]
outputs = [{"answer": output_answer} for _, output_answer in examples ]

# Crear dataset en LangSmith
dataset = client.create_dataset(
    dataset_name="Platzi Store Dataset v2",
    description="Dataset para evaluar el agente de la tienda Platzi Store"
)

# Agregar ejemplos al dataset
client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

# Imprimir el ID del dataset creado
print(f"Dataset creado con el ID: {dataset.id}!")
