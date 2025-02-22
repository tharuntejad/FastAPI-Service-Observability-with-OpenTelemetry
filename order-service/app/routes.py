
import requests
from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from datetime import datetime
from app.core.config import settings

import logging
from opentelemetry import trace
from opentelemetry.propagate import inject, extract
from opentelemetry.semconv.trace import SpanAttributes  # add semantic convention attributes to spans


# Set up logger
logger = logging.getLogger(settings.service_name)

# Get tracer instance
tracer = trace.get_tracer(__name__)

# Add an router
order_router = APIRouter()


# List all orders
@order_router.get("/list-orders")
def list_orders():
    # Start a new span for the list orders endpoint
    with tracer.start_as_current_span("list_orders_endpoint") as span:
        logger.info("Fetching all orders from the database.")
        try:
            conn = get_db_connection()
            cursor = conn.execute("SELECT * FROM orders")
            orders = cursor.fetchall()

            span.add_event("Orders fetched from database", attributes={"orders_count": len(orders)})
            span.set_attribute("orders_count", len(orders))
            span.set_status(trace.Status(trace.StatusCode.OK))

            logger.info(f"Fetched {len(orders)} orders.")
            return [{"username": order['username'], "product_name": order['product_name'], "order_date": order['order_date']} for order in orders]
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error("Failed to fetch orders.", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch orders")

# Request inventory service to list products
@order_router.get("/list-products")
def list_products():
    with tracer.start_as_current_span("list_products_endpoint") as span:
        logger.info("Fetching product list from inventory service.")

        headers = {}
        inject(headers)
        try:
            response = requests.get(f"{settings.inventory_service_url}/list-products", headers=headers)
            if response.status_code != 200:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Failed to fetch products"))
                logger.error("Failed to fetch products from inventory service.")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch products")

            span.add_event("Product list fetched successfully", attributes={"status_code": response.status_code})
            span.set_status(trace.Status(trace.StatusCode.OK))
            logger.info("Successfully fetched product list.")
            return response.json()
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error("Error occurred while fetching product list.", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch product list")

# Order a product
@order_router.post("/order-product")
def order_product(username: str, product_id: int):
    with tracer.start_as_current_span("order_product_endpoint") as span:
        # Add attributes to the span for better visibility
        span.set_attribute("username", username)
        span.set_attribute("product_id", product_id)

        logger.info(f"Received order request", extra={"username": username, "product_id": product_id})

        headers = {}
        inject(headers)
        try:
            response = requests.get(f"{settings.inventory_service_url}/list-products", headers=headers)
            products = response.json()

            product = next((p for p in products if p['id'] == product_id), None)
            if not product or product['stock'] <= 0:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Product unavailable"))
                logger.warning(f"Product with id={product_id} is unavailable.")
                raise HTTPException(status_code=400, detail="Product unavailable")

            conn = get_db_connection()
            conn.execute("""
            INSERT INTO orders (username, product_name, product_id, order_date)
            VALUES (?, ?, ?, ?)
            """, (username, product['name'], product_id, datetime.now().isoformat()))
            conn.commit()

            span.add_event("Order placed successfully", attributes={"product_id": product_id, "username": username})
            span.set_status(trace.Status(trace.StatusCode.OK))

            logger.info(f"Order placed successfully for product_id={product_id} by username={username}.")
            requests.post(f"{settings.inventory_service_url}/reduce-stock?product_id={product_id}", headers=headers)

            return {"message": "Order placed successfully"}
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error("Error occurred while placing order.", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to place order")
