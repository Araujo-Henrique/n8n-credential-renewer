from unittest.mock import MagicMock, patch

import requests

from notifier import send_status_message, send_telegram_message


def _fake_response(status_code=200, json_data=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"{status_code} erro"
        )
    else:
        response.raise_for_status.return_value = None
    return response


@patch("notifier.requests.post")
def test_send_telegram_message_monta_url_e_payload_certos(mock_post):
    mock_post.return_value = _fake_response(200, {"ok": True})

    send_telegram_message("123:ABC", "999", "ola")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.telegram.org/bot123:ABC/sendMessage"
    assert kwargs["json"] == {"chat_id": "999", "text": "ola"}


@patch("notifier.requests.post")
def test_send_status_message_sucesso_retorna_true(mock_post):
    mock_post.return_value = _fake_response(200, {"ok": True})

    resultado = send_status_message(
        success=True,
        detail="tudo certo",
        bot_token="123:ABC",
        chat_id="999",
    )

    assert resultado is True
    mock_post.assert_called_once()


@patch("notifier.requests.post")
def test_send_status_message_nunca_lanca_excecao(mock_post):
    mock_post.side_effect = requests.ConnectionError("sem rede")

    resultado = send_status_message(
        success=False,
        detail="playwright falhou",
        bot_token="123:ABC",
        chat_id="999",
    )

    assert resultado is False


@patch("notifier.requests.post")
def test_send_status_message_erro_http_retorna_false(mock_post):
    mock_post.return_value = _fake_response(
        400, {"ok": False, "description": "chat not found"}
    )

    resultado = send_status_message(
        success=True,
        detail="tudo certo",
        bot_token="123:ABC",
        chat_id="chat-errado",
    )

    assert resultado is False
