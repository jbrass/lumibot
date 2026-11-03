"""Alpaca labels every leg of a nested bracket order with the parent's order_class."""
from datetime import datetime, timezone
from uuid import UUID

from alpaca.trading.models import Order as ProviderOrder

from lumibot.brokers.alpaca import Alpaca
from lumibot.entities import Order


def _provider_order(number, side, order_type, order_class, legs=None, **prices):
    at = datetime(2027, 1, 4, tzinfo=timezone.utc)
    return ProviderOrder(
        id=UUID(int=number), client_order_id=f"neutral-{number}", asset_id=UUID(int=99),
        created_at=at, updated_at=at, submitted_at=at,
        symbol="SYN", asset_class="us_equity", qty="10", filled_qty="0",
        side=side, order_class=order_class, type=order_type, time_in_force="gtc",
        status="new", extended_hours=False, legs=legs, **prices,
    )


def test_bracket_parent_with_bracket_labelled_legs_parses():
    response = _provider_order(
        1, "sell", "market", "bracket", legs=[
            _provider_order(2, "buy", "limit", "bracket", limit_price="95"),
            _provider_order(3, "buy", "stop", "bracket", stop_price="105"),
        ],
    )
    broker = object.__new__(Alpaca)
    parent = broker._parse_broker_order(response, "strategy")
    assert parent.order_class == Order.OrderClass.BRACKET
    assert len(parent.child_orders) == 2
    assert all(child.order_class == Order.OrderClass.SIMPLE for child in parent.child_orders)
    assert [str(child.identifier) for child in parent.child_orders] == [str(UUID(int=2)), str(UUID(int=3))]


def test_bracket_order_without_legs_parses_as_simple():
    response = _provider_order(4, "buy", "limit", "bracket", limit_price="95")
    broker = object.__new__(Alpaca)
    order = broker._parse_broker_order(response, "strategy")
    assert order.order_class == Order.OrderClass.SIMPLE
