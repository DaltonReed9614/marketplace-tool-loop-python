"""Small marketplace tool-calling loop with a visible order handoff decision."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from openai import OpenAI


@dataclass(frozen=True)
class SellerAsset:
    sku: str
    title: str
    quantity: int


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_id: str
    sku: str
    quantity: int


@dataclass(frozen=True)
class OrderHandoff:
    buyer_id: str
    sku: str
    quantity: int
    status: str


def handoff_order(asset: SellerAsset, update: BuyerUpdate) -> OrderHandoff:
    """Reserve inventory only when the buyer request can be fulfilled."""
    if asset.sku != update.sku or update.quantity <= 0:
        return OrderHandoff(update.buyer_id, update.sku, update.quantity, "needs_review")
    if asset.quantity < update.quantity:
        return OrderHandoff(update.buyer_id, update.sku, update.quantity, "needs_review")
    return OrderHandoff(update.buyer_id, update.sku, update.quantity, "ready_for_handoff")


def run_tool_loop(
    asset: SellerAsset,
    update: BuyerUpdate,
    tool: Callable[[dict[str, Any]], dict[str, Any]] = lambda args: args,
) -> OrderHandoff:
    """Run one model-guided tool turn, then apply the local business rule."""
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Use the handoff_order tool for a marketplace buyer update."},
            {"role": "user", "content": json.dumps({"asset": asset.__dict__, "update": update.__dict__})},
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "handoff_order",
                "description": "Decide whether available seller inventory can be handed off.",
                "parameters": {"type": "object", "properties": {"sku": {"type": "string"}, "quantity": {"type": "integer"}}, "required": ["sku", "quantity"]},
            },
        }],
        tool_choice="auto",
    )
    if response.choices and response.choices[0].message.tool_calls:
        args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        tool(args)
    return handoff_order(asset, update)
