"""Procedural sound effects for 《现在》. Deterministic.
make(kind, **kw) -> stereo float32 array at 44.1 kHz."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
rng = np.random.default_rng(7)

def _bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)

def _lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)

def _verb(x, t=1.6, mix=.35):
    L = int(t * SR); ir = rng.standard_normal(L) * np.exp(-np.arange(L) / SR * (6.9 / t))
    ir = _lp(ir, 6000); w = fftconvolve(x, ir)[:len(x) + L]
    w /= np.max(np.abs(w)) + 1e-9; y = np.zeros(len(w)); y[:len(x)] = x * (1 - mix)
    return y + w * mix * np.max(np.abs(x))

def _st(m, pan0=0.0, pan1=0.0):
    p = np.linspace(pan0, pan1, len(m)); l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
    return np.stack([m * l, m * r], 1)

def shimmer(dur=1.6):
    """文字散开 / 粒子聚合：细沙般的高频闪烁"""
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * np.minimum(1, t / dur)) ** 1.5
    noise = _bp(rng.standard_normal(n), 3500, 11000) * env * .35
    grains = np.zeros(n)
    for _ in range(int(dur * 70)):
        s = rng.integers(0, n - 2000); f = rng.uniform(2500, 7000); g = int(rng.uniform(.01, .04) * SR)
        tt = np.arange(g) / SR; grains[s:s + g] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 90) * rng.uniform(.2, .6)
    m = _verb(noise + grains * env, 1.2, .4)
    return _st(m / np.max(np.abs(m)), -.3, .3)

def ticker(dur=1.2, count=14, end_ding=True):
    """数字转动：细密滴答，结尾一声轻响"""
    n = int((dur + (1.4 if end_ding else .2)) * SR); m = np.zeros(n)
    u = np.linspace(0, 1, count); times = (u - np.sin(2 * np.pi * u) / (2 * np.pi)) * dur  # ease in-out spacing
    for k, tk in enumerate(times):
        s = int(tk * SR); g = int(.012 * SR); tt = np.arange(g) / SR
        click = (np.sin(2 * np.pi * 3200 * tt) + .5 * np.sin(2 * np.pi * 5100 * tt)) * np.exp(-tt * 420)
        m[s:s + g] += click * (.5 + .3 * np.sin(k))
    if end_ding:
        s = int(dur * SR); g = int(1.3 * SR); tt = np.arange(g) / SR
        ding = (np.sin(2 * np.pi * 1318 * tt) + .4 * np.sin(2 * np.pi * 2637 * tt) + .2 * np.sin(2 * np.pi * 1318 * 2.76 * tt)) * np.exp(-tt * 3.5)
        m[s:s + g] += ding * .55
    m = _verb(m, 1.0, .25)
    return _st(m / np.max(np.abs(m)))

def whoosh(dur=1.0, pan0=-.7, pan1=.7):
    """光点飞行：一道轻的“嗖”，左右声像随方向移动"""
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    env = np.sin(np.pi * t / dur) ** 2
    lo = _bp(x, 400, 1800); hi = _bp(x, 1800, 6000)
    k = t / dur; m = (lo * (1 - k) + hi * k) * env
    m = _verb(m, .9, .3)
    return _st(m / np.max(np.abs(m)), pan0, pan1)

def sweep(dur=1.4):
    """数轴 / 横线展开：柔和上扬的气声"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 180 * 2 ** (t / dur * 1.5); ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + .3 * np.sin(2 * ph)) * np.sin(np.pi * t / dur) ** 2 * .5
    air = _bp(rng.standard_normal(n), 2000, 7000) * np.sin(np.pi * t / dur) ** 2 * .25
    m = _verb(tone + air, 1.5, .4)
    return _st(m / np.max(np.abs(m)), -.4, .4)

def chime(dur=4.0, f0=659.25):
    """安静处：很淡的一声长音"""
    n = int(dur * SR); t = np.arange(n) / SR
    m = (np.sin(2 * np.pi * f0 * t) + .25 * np.sin(2 * np.pi * f0 * 2 * t) + .12 * np.sin(2 * np.pi * f0 * 3.01 * t)) * np.exp(-t * 1.1) * np.minimum(1, t / .02)
    m = _verb(m, 3.0, .5)
    return _st(m / np.max(np.abs(m)))

def click(dur=.4):
    """（仅供参考，不建议使用）闪光的一声"""
    n = int(dur * SR); t = np.arange(n) / SR
    m = _bp(rng.standard_normal(n), 2000, 9000) * np.exp(-t * 60)
    return _st(m / np.max(np.abs(m)))

def thud(dur=2.5):
    """情绪落点：一声很低、很软的下沉"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 90 * np.exp(-t * .4); ph = 2 * np.pi * np.cumsum(f) / SR
    m = np.sin(ph) * np.exp(-t * 1.6) * np.minimum(1, t / .03)
    m = _verb(m, 2.0, .35)
    return _st(m / np.max(np.abs(m)))

KINDS = dict(shimmer=shimmer, ticker=ticker, whoosh=whoosh, sweep=sweep, chime=chime, click=click, thud=thud)
GAIN = dict(shimmer=.22, ticker=.20, whoosh=.22, sweep=.18, chime=.14, click=.18, thud=.30)  # relative to music peak .707

def make(kind, **kw):
    return KINDS[kind](**kw) * GAIN[kind]
