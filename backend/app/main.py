"""
FastAPI application entrypoint.
"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    addresses,
    admin,
    auth,
    cart,
    categories,
    checkout,
    health,
    orders,
    payments,
    product_images,
    products,
)
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aari_works")

# Ensure the upload directory exists before StaticFiles tries to mount it —
# a missing directory would make the mount fail at startup.
os.makedirs(os.path.join(settings.local_upload_dir, "products"), exist_ok=True)

app = FastAPI(title="Aari Works API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(addresses.router)
app.include_router(checkout.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(product_images.router)

# Serves uploaded files directly during local development. In Phase 18,
# Nginx will proxy /uploads to the backend rather than the browser
# hitting this port directly — the URL shape (/uploads/products/...)
# stays identical either way, so no stored image_url ever needs rewriting.
app.mount(
    "/uploads",
    StaticFiles(directory=settings.local_upload_dir),
    name="uploads",
)
