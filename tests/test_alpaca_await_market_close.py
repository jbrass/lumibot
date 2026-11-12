"""Live Alpaca: awaiting the close must not call a backtesting-only method.

_await_market_to_close called self.process_pending_orders(), which only
BacktestingBroker defines; the AttributeError crashed the strategy and the
executor restarted the session every ~30 seconds until the bell.
"""
from lumibot.brokers.alpaca import Alpaca


def test_await_market_to_close_without_process_pending_orders():
    broker = object.__new__(Alpaca)
    broker.get_time_to_close = lambda: 0
    assert not hasattr(broker, "process_pending_orders")
    broker._await_market_to_close(timedelta=5, strategy=None)  # no AttributeError
