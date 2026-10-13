"""mixaudio.py events.json bgm.wav dur out.wav  — music + procedural SFX"""
import sys, json, numpy as np
from scipy.io import wavfile
sys.path.insert(0, '.')
import sfx
ev = json.load(open(sys.argv[1])); dur = float(sys.argv[3]); SR = 44100; N = int(dur * SR)
sr, bg = wavfile.read(sys.argv[2]); bg = bg.astype(np.float64)[:N] / 32767 * .8
mix = np.zeros((N, 2)); mix[:len(bg)] += bg
for k, t, o in ev:
    if t >= dur: continue
    a = sfx.make(k, **o); s = int(t * SR); e = min(N, s + len(a)); mix[s:e] += a[:e - s]
mix *= .89 / np.max(np.abs(mix))
wavfile.write(sys.argv[4], SR, (mix * 32767).astype(np.int16)); print("ok", round(np.max(np.abs(mix)), 3))
