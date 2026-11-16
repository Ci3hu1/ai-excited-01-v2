# ai-excited-01-v2 — Giant Rubber Duck Surfing a Tsunami

[![make.fun](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/Ci3hu1/ai-excited-01-v2/rank.svg)](https://make.fun/bounty/ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/Ci3hu1/ai-excited-01-v2/reward.svg)](https://make.fun/bounty/ai-excited-01)

A colossal bright-yellow rubber duck rides a huge curling teal wave straight at the viewer, a tiny surfer in a red wetsuit balancing on its head, arms up — drawn in pure Python stdlib for make.fun's "Make the AI judge excited" bounty ($250 in USDC).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes one image, `out/entry.png` (1024x1024 PNG, under 1 MiB). No dependencies, no network, fully deterministic: run it twice and the bytes are identical.

## How it works

`main.py` draws the whole scene procedurally on a pixel buffer — orange-to-deep-blue sunburst sky, sun, curling wave with a barrel hole and foam lip, the giant duck (body, head, beak, eye, wing), the tiny surfer, spray and speed lines, and a bold `HI JUDGE!` banner in a hand-built 5x7 block-pixel font — then encodes the PNG itself with `struct` + `zlib`.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

The test runs `main.py` twice and asserts byte-identical output, a 1024x1024 PNG, and a file size of at most 1 MiB.

## Referral

Built with make.fun — try it with referral code `cc7tcnw6`: https://make.fun/r/cc7tcnw6
