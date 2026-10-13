# vibevideo

Vibe知识大赏风格知识短视频的制作 skill(默认易经风格,1080p60)。

- `SKILL.md`:skill 本体(流程、规则、默认风格包)。
- `toolkit/`:配套模板与脚本(HyperFrames 模板、配乐/音效/混音脚本、字体与 GSAP)。

安装:`npx skills add freyaxfreya/vibevideo -g`(Codex 实际装到 `~/.agents/skills/vibe-video`)。

渲染需要:Node、Chromium、ffmpeg、Python(numpy、scipy、playwright)、tmux 或等价的后台运行方式。

说明:`toolkit/assets/gsap.min.js` 没有放进本仓库(再分发条款作者尚未核实)。使用前请在 `toolkit/assets/` 下放入 gsap.min.js,例如 `npm i gsap` 后复制 `node_modules/gsap/dist/gsap.min.js`。
