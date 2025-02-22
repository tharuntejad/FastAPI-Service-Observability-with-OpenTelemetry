from pydantic import BaseModel

class Order(BaseModel):
    username: str
    product_name: str
    product_id: int
    order_date: str
