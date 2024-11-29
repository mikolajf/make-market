import json

import pytest
import zmq.asyncio
from make_market.ws_client import WebSocketConnectAsync


@pytest.fixture
def publisher_socket():
    return zmq.asyncio.Socket(zmq.asyncio.Context(), zmq.PUB)


@pytest.fixture
def config():
    return {"symbol1": True, "symbol2": False}


@pytest.fixture
def websocket_connect_async(publisher_socket, config):
    return WebSocketConnectAsync("ws://test_url", config, publisher_socket)


@pytest.mark.asyncio
async def test_subscribe_to_new_symbol(mocker, websocket_connect_async):
    mock_send = mocker.patch.object(
        websocket_connect_async, "_send", new_callable=mocker.AsyncMock
    )
    await websocket_connect_async._subscribe_to_new_symbol("symbol1")  # noqa: SLF001
    mock_send.assert_called_once_with(
        json.dumps({"action": "subscribe", "symbol": "symbol1"})
    )


@pytest.mark.asyncio
async def test_unsubscribe_from_symbol(mocker, websocket_connect_async):
    mock_send = mocker.patch.object(
        websocket_connect_async, "_send", new_callable=mocker.AsyncMock
    )
    await websocket_connect_async._unsubscribe_from_symbol("symbol1")  # noqa: SLF001
    mock_send.assert_called_once_with(
        json.dumps({"action": "unsubscribe", "symbol": "symbol1"})
    )


@pytest.mark.asyncio
async def test_send(mocker, websocket_connect_async):
    websocket_connect_async.websocket = mocker.AsyncMock()
    await websocket_connect_async._send("test_message")  # noqa: SLF001
    websocket_connect_async.websocket.send.assert_called_once_with("test_message")


@pytest.mark.asyncio
async def test_receive(mocker, websocket_connect_async):
    websocket_connect_async.websocket = mocker.AsyncMock()
    websocket_connect_async.websocket.recv = mocker.AsyncMock(
        return_value=json.dumps({"key": "value"})
    )
    response = await websocket_connect_async._receive()  # noqa: SLF001
    assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_send_receive(mocker, websocket_connect_async):
    mock_send = mocker.patch.object(
        websocket_connect_async, "_send", new_callable=mocker.AsyncMock
    )
    mock_receive = mocker.patch.object(
        websocket_connect_async, "_receive", new_callable=mocker.AsyncMock
    )
    mock_receive.return_value = {"key": "value"}
    response = await websocket_connect_async._send_receive("test_message")  # noqa: SLF001
    mock_send.assert_called_once_with("test_message")
    mock_receive.assert_called_once()
    assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_connect(mocker, websocket_connect_async):
    mock_connect = mocker.patch("websockets.connect", new_callable=mocker.AsyncMock)
    websocket_connect_async.config = {"symbol1": True}
    await websocket_connect_async.connect()
    mock_connect.assert_called_once_with("ws://test_url")
    assert websocket_connect_async.websocket is not None


@pytest.mark.asyncio
async def test_disconnect(mocker, websocket_connect_async):
    websocket_connect_async.websocket = mocker.AsyncMock()
    await websocket_connect_async.disconnect()
    assert websocket_connect_async.websocket is None


@pytest.mark.asyncio
async def test_start(mocker, websocket_connect_async):
    mock_connect = mocker.patch.object(
        websocket_connect_async, "connect", new_callable=mocker.AsyncMock
    )
    mock_main_loop = mocker.patch.object(
        websocket_connect_async, "_main_loop", new_callable=mocker.AsyncMock
    )
    await websocket_connect_async.start()
    mock_connect.assert_called_once()
    mock_main_loop.assert_called_once()


@pytest.mark.asyncio
async def test_stop(mocker, websocket_connect_async):
    mock_disconnect = mocker.patch.object(
        websocket_connect_async, "disconnect", new_callable=mocker.AsyncMock
    )
    await websocket_connect_async.stop()
    mock_disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_on_config_change(mocker, websocket_connect_async):
    new_config = {"symbol1": False, "symbol2": True}
    mock_subscribe = mocker.patch.object(
        websocket_connect_async,
        "_subscribe_to_new_symbol",
        new_callable=mocker.AsyncMock,
    )
    mock_unsubscribe = mocker.patch.object(
        websocket_connect_async,
        "_unsubscribe_from_symbol",
        new_callable=mocker.AsyncMock,
    )
    await websocket_connect_async.on_config_change(new_config)
    mock_unsubscribe.assert_called_once_with("symbol1")
    mock_subscribe.assert_called_once_with("symbol2")
    assert websocket_connect_async.config == new_config
