from __future__ import annotations

import json
import signal
import time
from pathlib import Path

try:
    from gnuradio import blocks, channels, gr, zeromq  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    blocks = channels = gr = zeromq = None

try:
    import zmq  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    zmq = None


class _StopFlag:
    stopped = False


def _install_signal_handlers() -> _StopFlag:
    flag = _StopFlag()

    def handler(*_: object) -> None:
        flag.stopped = True

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return flag


def _write_status(profile: dict, mode: str) -> None:
    out = Path("outputs/runtime/channel_status.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"mode": mode, "profile": profile}, indent=2), encoding="utf-8")


def _run_dummy(profile: dict) -> None:
    flag = _install_signal_handlers()
    _write_status(profile, str(profile.get("mode_hint", "dummy")))
    while not flag.stopped:
        time.sleep(1.0)


def _bridge_pair(ctx: "zmq.Context", source_endpoint: str, sink_endpoint: str) -> tuple["zmq.Socket", "zmq.Socket"]:
    assert zmq is not None
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    sub.connect(source_endpoint)
    pub = ctx.socket(zmq.PUB)
    pub.bind(sink_endpoint)
    return sub, pub


def _run_zmq_bridge(profile: dict) -> None:
    if zmq is None:
        _run_dummy(profile)
        return

    flag = _install_signal_handlers()
    ctx = zmq.Context()
    dl_sub, dl_pub = _bridge_pair(ctx, "tcp://127.0.0.1:2000", "tcp://127.0.0.1:2003")
    ul_sub, ul_pub = _bridge_pair(ctx, "tcp://127.0.0.1:2002", "tcp://127.0.0.1:2001")
    poller = zmq.Poller()
    poller.register(dl_sub, zmq.POLLIN)
    poller.register(ul_sub, zmq.POLLIN)
    _write_status(profile, "zmq-bridge")

    try:
        while not flag.stopped:
            events = dict(poller.poll(100))
            if dl_sub in events:
                dl_pub.send_multipart(dl_sub.recv_multipart())
            if ul_sub in events:
                ul_pub.send_multipart(ul_sub.recv_multipart())
    finally:
        for sock in (dl_sub, dl_pub, ul_sub, ul_pub):
            sock.close(0)
        ctx.term()


def _build_direction(tb: "gr.top_block", source_endpoint: str, sink_endpoint: str, sample_rate: float, noise: float, freq_offset_hz: float, delay_ms: float) -> None:
    assert gr and blocks and channels and zeromq
    src = zeromq.sub_source(gr.sizeof_gr_complex, 1, source_endpoint, 100, False, -1)
    chan = channels.channel_model(
        noise_voltage=noise,
        frequency_offset=(freq_offset_hz / sample_rate) if sample_rate else 0.0,
        epsilon=1.0,
    )
    delay = blocks.delay(gr.sizeof_gr_complex, int((sample_rate * delay_ms) / 1000.0))
    sink = zeromq.pub_sink(gr.sizeof_gr_complex, 1, sink_endpoint, 100, False, -1)
    tb.connect(src, chan, delay, sink)


def run_channel(profile: dict) -> None:
    if (
        not profile.get("awgn_enabled")
        and not profile.get("fading_enabled")
        and float(profile.get("delay_ms", 0.0)) == 0.0
        and float(profile.get("jitter_ms", 0.0)) == 0.0
        and float(profile.get("freq_offset_hz", 0.0)) == 0.0
        and float(profile.get("ul_loss_pct", 0.0)) == 0.0
        and float(profile.get("dl_loss_pct", 0.0)) == 0.0
    ):
        _run_zmq_bridge(profile)
        return

    if not all([blocks, channels, gr, zeromq]):
        _run_dummy(profile)
        return

    sample_rate = float(profile.get("sample_rate", 5.76e6))
    noise = float(profile.get("noise_voltage", 0.0)) if profile.get("awgn_enabled") else 0.0
    freq_offset = float(profile.get("freq_offset_hz", 0.0))
    delay_ms = float(profile.get("delay_ms", 0.0))
    ul_noise = noise + float(profile.get("ul_loss_pct", 0.0)) / 200.0
    dl_noise = noise + float(profile.get("dl_loss_pct", 0.0)) / 200.0

    try:
        tb = gr.top_block("nr_sitl_channel")
        _build_direction(tb, "tcp://127.0.0.1:2000", "tcp://127.0.0.1:2003", sample_rate, dl_noise, freq_offset, delay_ms)
        _build_direction(tb, "tcp://127.0.0.1:2002", "tcp://127.0.0.1:2001", sample_rate, ul_noise, freq_offset, delay_ms)
        _write_status(profile, "gnuradio-live")
        tb.start()
        flag = _install_signal_handlers()
        while not flag.stopped:
            time.sleep(1.0)
        tb.stop()
        tb.wait()
    except Exception:
        _run_dummy(profile)
