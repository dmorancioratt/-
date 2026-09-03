import base64

import pytest

from app.services import xunfei_virtual_human as vms


@pytest.fixture(autouse=True)
def clear_sessions():
    with vms._sessions_lock:
        vms._sessions.clear()
    yield
    with vms._sessions_lock:
        vms._sessions.clear()


def test_signed_url_contains_hmac_parameters(monkeypatch):
    monkeypatch.setattr(vms, "API_KEY", "test-key")
    monkeypatch.setattr(vms, "API_SECRET", "test-secret")
    url = vms._signed_url("/v1/private/vms2d_start")
    assert "host=" in url
    assert "date=" in url
    assert "authorization=" in url
    assert "test-secret" not in url


def test_start_speak_ping_and_stop(monkeypatch, tmp_path):
    monkeypatch.setattr(vms, "SERVICE_ID", "test-service")
    monkeypatch.setattr(vms, "APP_ID", "test-app")
    monkeypatch.setattr(vms, "API_KEY", "test-key")
    monkeypatch.setattr(vms, "API_SECRET", "test-secret")
    calls = []

    def fake_post(path, payload):
        calls.append((path, payload))
        if path.endswith("start"):
            return {
                "header": {"code": 0, "session": "remote-session", "sid": "start-sid"},
                "payload": {"stream_url": {"text": base64.b64encode(b"rtmp://example/live/1").decode()}},
            }
        return {"header": {"code": 0, "message": "success", "sid": "control-sid"}}

    monkeypatch.setattr(vms, "_post", fake_post)
    monkeypatch.setattr(vms, "_start_hls_transcoder", lambda _url, _handle: (tmp_path, None))
    started = vms.start_session("user-1")
    assert started["stream_url"] == "rtmp://example/live/1"
    assert started["capabilities"]["avatar_driver"] == "connected"
    assert "service_id" not in calls[0][1]["header"]

    spoken = vms.speak(started["session_id"], "你好，欢迎参加面试。")
    assert spoken["status"] == "speaking"
    encoded_text = calls[-1][1]["payload"]["text"]["text"]
    assert base64.b64decode(encoded_text).decode() == "你好，欢迎参加面试。"
    assert "service_id" not in calls[-1][1]["header"]
    assert "seq" not in calls[-1][1]["payload"]["text"]
    assert "seq" not in calls[-1][1]["payload"]["ctrl_w"]

    assert vms.ping_session(started["session_id"])["status"] == "alive"
    assert vms.stop_session(started["session_id"])["status"] == "stopped"
    assert [item[0] for item in calls] == [
        "/v1/private/vms2d_start",
        "/v1/private/vms2d_ctrl",
        "/v1/private/vms2d_ping",
        "/v1/private/vms2d_stop",
    ]


def test_unknown_session_is_rejected():
    with pytest.raises(vms.VirtualHumanError, match="不存在或已过期"):
        vms.speak("missing", "hello")
