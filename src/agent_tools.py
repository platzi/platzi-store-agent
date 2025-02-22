import json
from langsmith import traceable

@traceable
def calcular_precio(product_id: int, cantidad: int) -> str:
    """
    Calcula el precio total de un producto según su ID y cantidad.
    """
    with open("data/products.json") as f:
        products = json.load(f)
    
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Producto no encontrado."
    
    total_price = product["price"] * cantidad
    return f"El precio total de {cantidad} x {product['name']} es ${total_price:.2f}."

@traceable
def buscar_productos(search_term: str) -> str:
    """
    Busca productos cuyo nombre coincida con el término.
    """
    with open("data/products.json") as f:
        products = json.load(f)
        # Simular un error en la extracción de productos
        # raise Exception("Error en la extracción de productos")
    
    matching_products = [p for p in products if search_term.lower() in p["name"].lower()]
    
    if not matching_products:
        return f"No se encontraron productos que coincidan con el término de búsqueda: {search_term}"
    
    result_list = "\n".join([f"{p['id']}: {p['name']} (${p['price']})" for p in matching_products])
    return f"Productos encontrados:\n{result_list}"

@traceable
def sumar_precios(precios: list[float]) -> str:
    """
    Suma una lista de precios y regresa el total.
    """
    if not precios:
        return "No hay precios para sumar."
    return f"La suma total de los precios es: ${sum(precios):.2f}"

@traceable
def verificar_descuento(product_id: int) -> str:
    """
    Verifica si un producto tiene descuento y muestra su precio con descuento.
    """
    with open("data/products.json") as f:
        products = json.load(f)
    with open("data/discounts.json") as f:
        discounts = json.load(f)
    
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Producto no encontrado."
    
    discount = next((d for d in discounts if d["id"] == product_id), None)
    if not discount:
        return f"El producto {product['name']} no tiene descuento. Precio normal: ${product['price']:.2f}"
    
    discount_amount = product['price'] * discount['discount']
    final_price = product['price'] - discount_amount
    return (
        f"¡El producto {product['name']} tiene un {int(discount['discount'] * 100)}% de descuento!\n"
        f"Precio original: ${product['price']:.2f}\n"
        f"Descuento: ${discount_amount:.2f}\n"
        f"Precio final: ${final_price:.2f}"
    )
