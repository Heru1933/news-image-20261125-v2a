# news-image-20261125-v2a

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Heru1933/news-image-20261125-v2a/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Heru1933/news-image-20261125-v2a/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

THE BRUSSELS FILE — a magazine of Wednesday 25 November 2026. 40
stories, all hard news (war, trade, disaster, politics) whose events
happened on 25 November 2026, each verified against its source and each
with its source printed beside it. Pure Python standard library renderer
(no Pillow): bitmap fonts, a raw-RGB still blitter, a small canvas and a
PNG encoder. Deep blue, gold and cream: a masthead naming the day, a hero
story (the EU unveils a 50-billion-euro fund for AI and quantum
computing) with its toon illustration, a deck and a small Europe locator
map, seven illustrated features in a 4 + 3 grid (the Hormuz tanker
mines, the Ras Tanura refinery strike, the tariff salvo, the Ukraine
blackout, US GDP growth, the Bogor mine flood, the nor'easter), and the
full numbered list of all 40 stories. The eight illustrations are toon
stills rendered from a Remotion + Three.js engine, each a different
scene. Fully deterministic — two runs write byte-identical PNGs.

## Run it

```sh
python3 main.py
```

Writes `entry.png` (1024x1024) to `MAKEFUN_OUTPUT_DIR` when set, otherwise to `output/`.
