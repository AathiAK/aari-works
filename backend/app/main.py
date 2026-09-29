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

os.makedirs(os.path.join(settings.local_upload_dir, "products"), exist_ok=True)

app = FastAPI(title="Aari Works API", version="0.1.0")

# Tightened from Phase 5's allow_origins=["*"]: an explicit list is both
# more correct (wildcard + credentials is disallowed by browsers in
# credentialed mode) and scoped to exactly what should be able to call
# this API. Add production origins to CORS_ORIGINS in .env, not here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
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

app.mount(
    "/uploads",
    StaticFiles(directory=settings.local_upload_dir),
    name="uploads",
)
