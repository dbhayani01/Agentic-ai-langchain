from langchain_core.tools import tool

MOCK_ORDERS = {
    "ORD-1001": {"status": "shipped", "eta": "2026-07-02"},
    "ORD-1002": {"status": "processing", "eta": "2026-07-05"},
}

MOCK_PRODUCTS = [
    {"id": "SKU-001", "name": "Noise-Canceling Headphones", "price": 199},
    {"id": "SKU-002", "name": "Wireless Ergonomic Mouse", "price": 59},
    {"id": "SKU-003", "name": "4K USB-C Monitor", "price": 349},
]

FAQ = {
    "returns": "You can return products within 30 days of delivery.",
    "refund": "Refunds are processed within 5-7 business days after inspection.",
    "shipping": "Standard shipping takes 3-5 business days.",
}


@tool
async def order_status_checker(order_id: str) -> str:
    """Get order status and ETA by order id."""
    order = MOCK_ORDERS.get(order_id)
    if not order:
        return f"No order found for {order_id}."
    return f"Order {order_id} is {order['status']}. Estimated delivery: {order['eta']}."


@tool
async def product_search(query: str) -> str:
    """Search products by a user query."""
    query_l = query.lower()
    matches = [p for p in MOCK_PRODUCTS if query_l in p["name"].lower()]
    if not matches:
        return "No products matched your query."
    return " | ".join(f"{m['name']} (${m['price']}) [id: {m['id']}]" for m in matches)


@tool
async def faq_retriever(topic: str) -> str:
    """Retrieve a FAQ answer for a support topic such as shipping, returns, or refund."""
    topic_l = topic.lower()
    for key, answer in FAQ.items():
        if key in topic_l:
            return answer
    return "I couldn't find a FAQ entry for that topic."
