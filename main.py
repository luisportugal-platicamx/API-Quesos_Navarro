from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI(
    title="API de Cobranza - Quesos Navarro",
    description="Mockup para la gestión automatizada de pagos, saldos y conciliación"
)

# --- MODELOS DE DATOS (Validación) ---

class Customer(BaseModel):
    customerId: str
    customerName: str
    contactName: str
    phone: str
    amountDue: float
    currency: str
    dueDate: str
    status: str

class QueryBalance(BaseModel):
    phone: str

    # Este validador intercepta el teléfono y lo limpia automáticamente
    @field_validator('phone')
    @classmethod
    def clean_phone_number(cls, value: str) -> str:
        clean_val = value.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
        if not clean_val.startswith("+"):
            clean_val = "+" + clean_val
        return clean_val

class PaymentLinkRequest(BaseModel):
    customerId: str
    amount: float
    concept: str

class InteractionLog(BaseModel):
    customerId: str
    channel: str
    event: str
    notes: str

class TransactionHistoryRequest(BaseModel):
    customerId: str
    limit: Optional[int] = 5  # Por defecto trae los últimos 5 movimientos

# --- BASES DE DATOS MOCK ---

customers_db = {
    "+523781134353": {
        "customerId": "CUST-001",
        "customerName": "Quesos Navarro (Sede)",
        "contactName": "Guadalupe Calderón",
        "phone": "+523781134353",
        "amountDue": 1000.00,
        "currency": "MXN",
        "dueDate": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        "status": "upcoming_due"
    },
    "+523338082757": {
        "customerId": "CUST-002",
        "customerName": "Distribuidora Hipólito",
        "contactName": "Miguel Hipólito",
        "phone": "+523338082757",
        "amountDue": 1000.00,
        "currency": "MXN",
        "dueDate": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        "status": "upcoming_due"
    },
    "+523781869388": {
        "customerId": "CUST-003",
        "customerName": "Abarrotes Angela",
        "contactName": "Angela Padilla",
        "phone": "+523781869388",
        "amountDue": 1000.00,
        "currency": "MXN",
        "dueDate": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        "status": "upcoming_due"
    }
}

transactions_db = {
    "CUST-001": [
        {"transactionId": "PAY-901", "date": "2026-04-28", "type": "payment", "amount": 500.00, "description": "Abono vía transferencia", "status": "applied"},
        {"transactionId": "INV-304", "date": "2026-04-15", "type": "invoice", "amount": 1500.00, "description": "Compra Queso Oaxaca 10kg", "status": "partially_paid"}
    ],
    "CUST-002": [
        {"transactionId": "INV-305", "date": "2026-04-20", "type": "invoice", "amount": 1000.00, "description": "Compra Queso Panela 5kg", "status": "pending"}
    ]
}

# --- ENDPOINTS ---

@app.post("/collections/upcoming-due", response_model=dict)
async def get_upcoming_due(daysBeforeDue: int = 3):
    """Endpoint A: Obtener clientes próximos a vencer"""
    upcoming = list(customers_db.values())
    return {"success": True, "data": upcoming}

@app.post("/collections/customer-balance")
async def get_balance(query: QueryBalance):
    """Endpoint B: Consultar saldo por número de teléfono"""
    # Gracias al field_validator, 'query.phone' ya viene limpio y con el '+'
    customer = customers_db.get(query.phone)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {"success": True, "data": customer}

@app.post("/collections/generate-payment-link")
async def generate_link(req: PaymentLinkRequest):
    """Endpoint C: Generar liga de pago simulada"""
    link = f"https://pagos.quesosnavarro.com/pay/{req.customerId}/{req.amount}"
    return {
        "success": True,
        "data": {
            "paymentLink": link,
            "expiresAt": (datetime.now() + timedelta(hours=24)).isoformat()
        }
    }

@app.post("/collections/log-interaction")
async def log_interaction(log: InteractionLog):
    """Endpoint D: Registrar evento en el log"""
    print(f"DEBUG: Registro para {log.customerId} vía {log.channel} - Evento: {log.event}")
    return {"success": True, "data": {"logged": True}}

@app.post("/collections/customer-transactions")
async def get_transactions(req: TransactionHistoryRequest):
    """Endpoint E: Obtener historial de movimientos (compras y pagos)"""
    history = transactions_db.get(req.customerId, [])
    
    if not history:
        return {"success": True, "message": "Sin movimientos recientes", "data": []}
    
    limited_history = history[:req.limit]
    return {"success": True, "data": limited_history}
