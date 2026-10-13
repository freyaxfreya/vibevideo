"""Original ambient pad + sparse bells for 《现在》. Deterministic. Usage: python3 bgm.py <seconds> <out.wav>"""
import sys, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
N = int(SR * dur); t = np.arange(N) / SR
rng = np.random.default_rng(20261009)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

# chord loop (MIDI), 8 s each
chords = [[50, 57, 61, 64, 66],   # Dmaj9
          [47, 54, 57, 61, 62],   # Bm(add9)
          [43, 50, 54, 59, 61],   # Gmaj7(#11)
          [45, 52, 57, 59, 64]]   # Asus2
CL = 8.0

def env(n, a, r):
    e = np.ones(n); A = min(int(a * SR), n // 2); R = min(int(r * SR), n - A)
    e[:A] = np.linspace(0, 1, A) ** 2
    if R > 0: e[n - R:] *= np.linspace(1, 0, R) ** 1.5
    return e

pad = np.zeros(N)
k = 0; start = 0.0
while start < dur:
    ch = chords[k % 4]
    seg = CL + 3.0                       # overlap for release
    n = min(int(seg * SR), N - int(start * SR))
    if n <= 0: break
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for m in ch:
        f = hz(m)
        for det in (-0.12, 0.0, 0.11):   # slight chorus
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * ff * tt + ph) + 0.25 * np.sin(4 * np.pi * ff * tt + ph) + 0.08 * np.sin(6 * np.pi * ff * tt)
    s *= env(n, 2.8, 3.2) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * tt))
    i = int(start * SR); pad[i:i + n] += s
    k += 1; start += CL

pad = sosfilt(butter(2, 1400, 'low', fs=SR, output='sos'), pad)
pad /= np.max(np.abs(pad)) + 1e-9

# sparse bells, D major pentatonic, upper register
scale = [74, 76, 78, 81, 83, 86, 88]
bells = np.zeros(N)
tb = 3.0
while tb < dur - 3:
    m = scale[rng.integers(len(scale))]
    f = hz(m); n = int(4.0 * SR); tt = np.arange(n) / SR
    b = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3)) * np.exp(-tt * 1.4)
    b *= np.minimum(1, tt / 0.004)
    i = int(tb * SR); j = min(N, i + n); bells[i:j] += b[:j - i] * rng.uniform(.5, .9)
    tb += rng.uniform(2.5, 5.5)
bells /= np.max(np.abs(bells)) + 1e-9

# low drone
drone = np.sin(2 * np.pi * hz(38) * t) * 0.5 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))

mix = 0.62 * pad + 0.22 * bells + 0.16 * drone

# reverb: synthetic exponential-decay noise IR, stereo
def ir(seed):
    r = np.random.default_rng(seed); L = int(3.2 * SR)
    x = r.standard_normal(L) * np.exp(-np.arange(L) / SR * 2.0)
    return sosfilt(butter(1, 5000, 'low', fs=SR, output='sos'), x)
wetL = fftconvolve(mix, ir(1))[:N]; wetR = fftconvolve(mix, ir(2))[:N]
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L = 0.55 * mix + 0.45 * wetL; R = 0.55 * mix + 0.45 * wetR
st = np.stack([L, R], 1)

# fades + normalise to -3 dBFS peak
fi, fo = int(2.0 * SR), int(3.5 * SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]
st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
st *= 0.707 / np.max(np.abs(st))
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print("wrote", out, dur, "s")
