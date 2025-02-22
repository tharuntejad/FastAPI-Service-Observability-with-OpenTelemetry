
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

# Initialize FastAPI app
inventory_router = APIRouter()


# List products from db
@inventory_router.get("/list-products")
def list_products():
    with tracer.start_as_current_span("list_products_endpoint") as span:
        logger.info("Fetching all products from the database.")
        span.add_event("Fetching all products from the database.")

        conn = get_db_connection()
        products = conn.execute("SELECT * FROM products").fetchall()
        logger.info(f"Fetched {len(products)} products from the database.")

        span.add_event(f"Fetched {len(products)} products from the database.")
        span.set_attribute("products_count", len(products))
        span.set_status(trace.Status(trace.StatusCode.OK))

        return [dict(product) for product in products]

# Reduce stock for a product
@inventory_router.post("/reduce-stock")
def reduce_stock(product_id: int):
    with tracer.start_as_current_span("reduce_stock_endpoint") as span:
        logger.info(f"Received request to reduce stock for product_id={product_id}.")
        span.add_event(f"Received request to reduce stock for product_id={product_id}.")

        conn = get_db_connection()
        product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

        # logger.info(product.keys())
        if not product:
            logger.warning(f"Product with id={product_id} does not exist.")
            raise HTTPException(status_code=400, detail="Product not found")

        if product["stock"] <= 0:
            logger.warning(f"Product with id={product_id} is out of stock.")
            raise HTTPException(status_code=400, detail="Product unavailable")

        conn.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))
        conn.commit()
        logger.info(f"Stock successfully reduced for product_id={product_id}.")

        span.add_event(f"Stock successfully reduced for product_id={product_id}.")
        span.set_status(trace.Status(trace.StatusCode.OK))

        return {"message": "Stock reduced"}
