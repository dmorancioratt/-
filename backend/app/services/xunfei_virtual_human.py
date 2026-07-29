import base64
import hashlib
import hmac
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from email.utils import formatdate
from pathlib import Path
from urllib.parse import urlencode, urlparse

import httpx

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass


BASE_URL = os.getenv("XUNFEI_VIRTUAL_HUMAN_BASE_URL", "https://vms.cn-huadong-1.xf-yun.com").rstrip("/")
APP_ID = os.getenv("XUNFEI_VIRTUAL_HUMAN_APP_ID", "").strip()
API_KEY = os.getenv("XUNFEI_VIRTUAL_HUMAN_API_KEY", "").strip()
API_SECRET = os.getenv("XUNFEI_VIRTUAL_HUMAN_API_SECRET", "").strip()
SERVICE_ID = os.getenv("XUNFEI_VIRTUAL_HUMAN_SERVICE_ID", "").strip()
AVATAR_ID = os.getenv("XUNFEI_VIRTUAL_HUMAN_AVATAR_ID", "118801001").strip()
VOICE = os.getenv("XUNFEI_VIRTUAL_HUMAN_VOICE", "x3_qianxue").strip()
STREAM_PROTOCOL = os.getenv("XUNFEI_VIRTUAL_HUMAN_STREAM_PROTOCOL", "rtmp").strip().lower()
REQUEST_TIMEOUT = float(os.getenv("XUNFEI_VIRTUAL_HUMAN_TIMEOUT_SECONDS", "30"))
SESSION_TTL_SECONDS = 90


class VirtualHumanError(RuntimeError):
    pass


@dataclass
class _Session:
    remote_session: str
    stream_url: str
    uid: str
    created_at: float
    touched_at: float
    media_dir: Path
    transcoder: subprocess.Popen | None


_sessions: dict[str, _Session] = {}
_sessions_lock = threading.Lock()


def is_configured() -> bool:
    return bool(APP_ID and API_KEY and API_SECRET and AVATAR_ID)


def virtual_human_status() -> dict:
    return {
        "provider": "xunfei",
        "configured": is_configured(),
        "service_id": _masked_identifier(SERVICE_ID),
        "avatar_id": AVATAR_ID if is_configured() else "",
        "voice": VOICE if is_configured() else "",
        "stream_protocol": STREAM_PROTOCOL,
        "playback": "hls-proxy" if STREAM_PROTOCOL == "rtmp" else "sdk-required",
        "capabilities": {
            "video_stream": "configured" if is_configured() else "missing-config",
            "tts": "configured" if is_configured() else "missing-config",
            "avatar_driver": "configured" if is_configured() else "missing-config",
            "asr": "not-in-this-api",
        },
    }


def start_session(uid: str = "") -> dict:
    _require_config()
    _remove_stale_sessions()
    safe_uid = (uid or f"skillbridge-{uuid.uuid4().hex[:12]}")[:32]
    existing = _find_session_by_uid(safe_uid)
    if existing is not None:
        handle, session = existing
        if session.transcoder is not None and session.transcoder.poll() is None:
            _touch_session(handle)
            return _session_response(handle, session)
        _pop_session(handle)
        try:
            _stop_remote_session(session)
        except VirtualHumanError:
            pass
        finally:
            _stop_local_media(session)
    payload = {
        "header": {"app_id": APP_ID, "uid": safe_uid},
        "parameter": {
            "vmr": {
                "stream": {"protocol": STREAM_PROTOCOL},
                "avatar_id": AVATAR_ID,
                "width": 1280,
                "height": 720,
            }
        },
    }
    response = _post("/v1/private/vms2d_start", payload)
    header = response.get("header") or {}
    remote_session = str(header.get("session") or "")
    stream_url = _extract_stream_url(response)
    if not remote_session or not stream_url:
        raise VirtualHumanError("讯飞返回成功，但响应中缺少会话或视频流地址")

    handle = uuid.uuid4().hex
    try:
        media_dir, transcoder = _start_hls_transcoder(stream_url, handle)
    except VirtualHumanError:
        try:
            _stop_remote_session(_Session(remote_session, stream_url, safe_uid, time.time(), time.time(), Path(), None))
        except VirtualHumanError:
            pass
        raise
    now = time.time()
    session = _Session(remote_session, stream_url, safe_uid, now, now, media_dir, transcoder)
    with _sessions_lock:
        _sessions[handle] = session
    return _session_response(handle, session)


def _session_response(handle: str, session: _Session) -> dict:
    return {
        "provider": "xunfei",
        "session_id": handle,
        "stream_url": session.stream_url,
        "stream_protocol": STREAM_PROTOCOL,
        "avatar_id": AVATAR_ID,
        "voice": VOICE,
        "heartbeat_interval_seconds": 30,
        "playback_url": f"/api/digital-interviewer/virtual-human/media/{handle}/index.m3u8",
        "playback_protocol": "hls",
        "playback_hint": "讯飞 RTMP 流已由后端实时转换为浏览器可播放的 HLS",
        "capabilities": {
            "video_stream": "connected",
            "tts": "connected",
            "avatar_driver": "connected",
            "asr": "not-in-this-api",
        },
    }


def speak(session_id: str, text: str) -> dict:
    content = text.strip()
    if not content:
        raise VirtualHumanError("数字人播报文本不能为空")
    if len(content.encode("utf-8")) > 65536:
        raise VirtualHumanError("数字人播报文本不能超过 64KB")
    session = _get_session(session_id)
    payload = {
        "header": {"app_id": APP_ID, "session": session.remote_session, "uid": session.uid},
        "parameter": {"tts": {"vcn": VOICE, "speed": 50, "pitch": 50, "volume": 50}},
        "payload": {
            "text": {
                "encoding": "utf8",
                "status": 3,
                "text": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            },
            "ctrl_w": {"encoding": "utf8", "format": "json", "status": 3},
        },
    }
    response = _post("/v1/private/vms2d_ctrl", payload)
    _touch_session(session_id)
    return {
        "provider": "xunfei",
        "session_id": session_id,
        "status": "speaking",
        "sid": str((response.get("header") or {}).get("sid") or ""),
    }


def ping_session(session_id: str) -> dict:
    session = _get_session(session_id)
    _post(
        "/v1/private/vms2d_ping",
        {"header": {"app_id": APP_ID, "session": session.remote_session, "uid": session.uid}},
    )
    _touch_session(session_id)
    return {"provider": "xunfei", "session_id": session_id, "status": "alive"}


def stop_session(session_id: str) -> dict:
    session = _pop_session(session_id)
    if session is None:
        return {"provider": "xunfei", "session_id": session_id, "status": "already-stopped"}
    try:
        _stop_remote_session(session)
    finally:
        _stop_local_media(session)
    return {"provider": "xunfei", "session_id": session_id, "status": "stopped"}


def stop_all_sessions() -> None:
    with _sessions_lock:
        sessions = list(_sessions.values())
        _sessions.clear()
    for session in sessions:
        try:
            _stop_remote_session(session)
        except VirtualHumanError:
            pass
        finally:
            _stop_local_media(session)


def cleanup_stale_sessions() -> None:
    _remove_stale_sessions()


def get_media_file(session_id: str, file_name: str) -> Path | None:
    if file_name != "index.m3u8" and not re.fullmatch(r"segment_\d{5}\.ts", file_name):
        return None
    session = _get_session(session_id)
    candidate = (session.media_dir / file_name).resolve()
    if candidate.parent != session.media_dir.resolve() or not candidate.is_file():
        return None
    _touch_session(session_id)
    return candidate


def _signed_url(path: str) -> str:
    parsed = urlparse(BASE_URL)
    host = parsed.netloc
    date = formatdate(usegmt=True)
    signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
    digest = hmac.new(API_SECRET.encode("utf-8"), signature_origin.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("ascii")
    authorization_origin = (
        f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("ascii")
    return f"{BASE_URL}{path}?{urlencode({'host': host, 'date': date, 'authorization': authorization})}"


def _post(path: str, payload: dict) -> dict:
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT, trust_env=False) as client:
            response = client.post(_signed_url(path), json=payload)
    except httpx.TimeoutException as exc:
        raise VirtualHumanError("讯飞数字人接口请求超时") from exc
    except httpx.HTTPError as exc:
        raise VirtualHumanError("无法连接讯飞数字人服务") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise VirtualHumanError(f"讯飞数字人接口返回了无效响应（HTTP {response.status_code}）") from exc
    header = data.get("header") or {}
    code = header.get("code")
    message = str(header.get("message") or data.get("message") or "未知错误")
    if response.status_code >= 400 or code not in (None, 0):
        if code == 11203:
            raise VirtualHumanError("讯飞数字人并发数已满，请先结束已有会话，稍后再试（code=11203）")
        if code == 100002:
            raise VirtualHumanError("讯飞限制会话结束后 60 秒内重复创建，请稍后再试（code=100002）")
        raise VirtualHumanError(f"讯飞数字人接口失败：{message}（code={code if code is not None else response.status_code}）")
    return data


def _extract_stream_url(response: dict) -> str:
    header = response.get("header") or {}
    if header.get("stream_url"):
        return str(header["stream_url"])
    stream_payload = (response.get("payload") or {}).get("stream_url") or {}
    encoded = stream_payload.get("text")
    if not encoded:
        return ""
    try:
        return base64.b64decode(encoded).decode("utf-8").strip()
    except (ValueError, UnicodeDecodeError):
        return ""


def _get_session(session_id: str) -> _Session:
    with _sessions_lock:
        session = _sessions.get(session_id)
    if session is None:
        raise VirtualHumanError("数字人会话不存在或已过期，请重新启动")
    return session


def _find_session_by_uid(uid: str) -> tuple[str, _Session] | None:
    with _sessions_lock:
        for handle, session in _sessions.items():
            if session.uid == uid:
                return handle, session
    return None


def _touch_session(session_id: str) -> None:
    with _sessions_lock:
        session = _sessions.get(session_id)
        if session:
            session.touched_at = time.time()


def _pop_session(session_id: str) -> _Session | None:
    with _sessions_lock:
        return _sessions.pop(session_id, None)


def _remove_stale_sessions() -> None:
    cutoff = time.time() - SESSION_TTL_SECONDS
    with _sessions_lock:
        stale_handles = [handle for handle, session in _sessions.items() if session.touched_at < cutoff]
        stale_sessions = [_sessions[handle] for handle in stale_handles]
        for handle in stale_handles:
            _sessions.pop(handle, None)
    for session in stale_sessions:
        try:
            _stop_remote_session(session)
        except VirtualHumanError:
            pass
        finally:
            _stop_local_media(session)


def _stop_remote_session(session: _Session) -> None:
    _post(
        "/v1/private/vms2d_stop",
        {"header": {"app_id": APP_ID, "session": session.remote_session, "uid": session.uid}},
    )


def _start_hls_transcoder(stream_url: str, handle: str) -> tuple[Path, subprocess.Popen]:
    try:
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError) as exc:
        raise VirtualHumanError("本机缺少数字人视频转码组件，请安装 imageio-ffmpeg") from exc

    media_dir = Path(tempfile.mkdtemp(prefix=f"skillbridge-vms-{handle[:8]}-"))
    playlist = media_dir / "index.m3u8"
    segment_pattern = media_dir / "segment_%05d.ts"
    command = [
        ffmpeg_exe,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        stream_url,
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-vf",
        "scale=960:-2",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "30",
        "-keyint_min",
        "30",
        "-sc_threshold",
        "0",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-f",
        "hls",
        "-hls_time",
        "1",
        "-hls_list_size",
        "6",
        "-hls_flags",
        "delete_segments+append_list+omit_endlist+independent_segments",
        "-hls_segment_filename",
        str(segment_pattern),
        str(playlist),
    ]
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        creationflags=creation_flags,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        if playlist.is_file() and any(media_dir.glob("segment_*.ts")):
            return media_dir, process
        if process.poll() is not None:
            detail = (process.stderr.read() if process.stderr else b"").decode("utf-8", errors="ignore").strip()
            _cleanup_media_dir(media_dir)
            raise VirtualHumanError(f"数字人视频转码启动失败：{detail[-300:] or 'FFmpeg 已退出'}")
        time.sleep(0.25)

    _terminate_process(process)
    _cleanup_media_dir(media_dir)
    raise VirtualHumanError("已连接讯飞视频流，但等待浏览器播放画面超时")


def _stop_local_media(session: _Session) -> None:
    if session.transcoder is not None:
        _terminate_process(session.transcoder)
    if session.media_dir:
        _cleanup_media_dir(session.media_dir)


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def _cleanup_media_dir(media_dir: Path) -> None:
    resolved = media_dir.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved.parent == temp_root and resolved.name.startswith("skillbridge-vms-"):
        shutil.rmtree(resolved, ignore_errors=True)


def _require_config() -> None:
    if not is_configured():
        raise VirtualHumanError("讯飞数字人配置不完整，请检查后端环境变量")


def _masked_identifier(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "*" * len(value)
    return f"{'*' * (len(value) - 6)}{value[-6:]}"
