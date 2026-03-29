"""
DataWhisperer - FastAPI Backend
Wraps the ADK agent and exposes REST endpoints for the frontend
"""

import os
import sys
import json
import uuid
import asyncio
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add adk_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "adk_agent"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from datawhisperer_app.agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DataWhisperer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Session management
session_service = InMemorySessionService()
APP_NAME = "datawhisperer"


class QueryRequest(BaseModel):
    message: str
    session_id: str = None


class SessionResponse(BaseModel):
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend HTML."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/session/new", response_model=SessionResponse)
async def new_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME,
        user_id="user",
        session_id=session_id,
    )
    logger.info(f"New session created: {session_id}")
    return SessionResponse(session_id=session_id)


@app.post("/query")
async def query_agent(req: QueryRequest):
    """Send a query to the DataWhisperer agent and stream the response."""

    session_id = req.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name=APP_NAME,
            user_id="user",
            session_id=session_id,
        )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    async def generate() -> AsyncGenerator[str, None]:
        try:
            message = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=req.message)],
            )

            full_response = ""
            sql_queries = []
            tool_calls = []

            async for event in runner.run_async(
                user_id="user",
                session_id=session_id,
                new_message=message,
            ):
                # Capture tool usage (MCP calls)
                if hasattr(event, "content") and event.content:
                    for part in event.content.parts:
                        # Tool call (SQL being executed)
                        if hasattr(part, "function_call") and part.function_call:
                            fc = part.function_call
                            tool_calls.append({
                                "tool": fc.name,
                                "args": dict(fc.args) if fc.args else {},
                            })
                            # Extract SQL from read_query calls
                            if fc.name == "read_query" and fc.args:
                                sql = fc.args.get("query", "")
                                if sql:
                                    sql_queries.append(sql)
                            # Stream tool call event
                            yield f"data: {json.dumps({'type': 'tool_call', 'tool': fc.name, 'args': dict(fc.args) if fc.args else {}})}\n\n"

                        # Final text response
                        if hasattr(part, "text") and part.text:
                            full_response += part.text

                # Stream final response when agent is done
                if event.is_final_response() and full_response:
                    yield f"data: {json.dumps({'type': 'response', 'text': full_response, 'sql_queries': sql_queries, 'session_id': session_id})}\n\n"

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "DataWhisperer", "version": "1.0.0"}


@app.get("/schema")
async def get_schema():
    """Return the database schema info for the frontend."""
    return {
        "tables": [
            {
                "name": "categories",
                "columns": ["id", "name", "description"],
                "description": "Product categories",
            },
            {
                "name": "products",
                "columns": ["id", "name", "category_id", "price", "cost", "stock_qty", "rating", "review_count"],
                "description": "Product catalog with pricing",
            },
            {
                "name": "customers",
                "columns": ["id", "name", "email", "city", "state", "joined_date", "tier"],
                "description": "Customer profiles with loyalty tier",
            },
            {
                "name": "orders",
                "columns": ["id", "customer_id", "order_date", "status", "shipping_city", "shipping_state", "total_amount", "payment_method"],
                "description": "Order transactions",
            },
            {
                "name": "order_items",
                "columns": ["id", "order_id", "product_id", "quantity", "unit_price", "discount_pct"],
                "description": "Line items within each order",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
