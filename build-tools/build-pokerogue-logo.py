#!/usr/bin/env python3
"""Showdown's "Pokémon Showdown! BETA" header logo, recoloured to PokéRogue's logo colours.

    python3 build-tools/build-pokerogue-logo.py

Reads play.pokemonshowdown.com/pokemonshowdownbeta.png and @2x.png and writes them to
play.pokemonshowdown.com/sprites-custom/logo/. Only the colours change; the logo is
still Showdown's own. PokéRogue's logo uses four colours, and they go where Showdown's
logo has its matching parts:
  - the blue letters     -> PokéRogue's blues, steel #346485 to navy #2e4069
  - the pale outline     -> PokéRogue's red outline, #da3838
  - the BETA badge       -> PokéRogue's maroon shadow colour, #671528 (lettering stays pale)
Needs Pillow.
"""
import colorsys
import os

from PIL import Image

PLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play.pokemonshowdown.com')
OUT = os.path.join(PLAY, 'sprites-custom', 'logo')

NAVY = (0x2e, 0x40, 0x69)
STEEL = (0x34, 0x64, 0x85)
RED = (0xda, 0x38, 0x38)
MAROON = (0x67, 0x15, 0x28)
HIGHLIGHT = (0x5b, 0x8d, 0xb3)  # a lighter step of the steel blue, for the letters' shine


def mix(a, b, t):
	t = max(0.0, min(1.0, t))
	return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def shade(colour, factor):
	"""lighten (factor > 1) or darken (< 1) a colour, keeping its hue"""
	h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in colour))
	return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, max(0, min(1, l * factor)), s))


def smoothstep(a, b, x):
	t = max(0.0, min(1.0, (x - a) / (b - a)))
	return t * t * (3 - 2 * t)


def badge_box(im):
	"""The BETA badge: the box around its slate-grey fill, plus its pale rim"""
	w, h = im.size
	px = im.load()
	xs, ys = [], []
	for y in range(h // 2, h):
		for x in range(w // 2, w):
			r, g, b, a = px[x, y]
			if a > 200 and abs(r - 0x3b) + abs(g - 0x4d) + abs(b - 0x62) <= 12:  # its flat #3b4d62
				xs.append(x)
				ys.append(y)
	pad = max(2, w // 90)
	return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def letter_colour(light):
	"""Showdown's blue letters, dark to light: navy, steel, then a lighter steel"""
	if light < 0.42:
		return mix(NAVY, STEEL, (light - 0.22) / 0.2)
	return mix(STEEL, HIGHLIGHT, (light - 0.42) / 0.26)


def recolour_pixel(rgba, badge):
	r, g, b, a = rgba
	if a == 0:
		return rgba
	hue, light, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
	hue *= 360
	if badge:
		if light >= 0.6:
			return (*mix((0xe8, 0xe0, 0xe4), (0xff, 0xff, 0xff), (light - 0.6) / 0.4), a)  # lettering and rim
		return (*shade(MAROON, light / 0.31), a)
	if sat < 0.32 and light < 0.5:
		return (*shade(MAROON, light / 0.31), a)  # dark edges and shadow
	if 170 <= hue <= 230 or light >= 0.72:
		# the letters blend into their pale outline, which becomes PokéRogue's red; how
		# white a pixel is tells the outline (#cee4f5) from the letters' shine (#61c5f5)
		outline = smoothstep(0.45, 0.72, min(r, g, b) / 255)
		return (*mix(letter_colour(min(light, 0.68)), shade(RED, 0.95 + 0.15 * outline), outline), a)
	return rgba


def recolour(src, dst):
	im = Image.open(src).convert('RGBA')
	x0, y0, x1, y1 = badge_box(im)
	px = im.load()
	for y in range(im.size[1]):
		for x in range(im.size[0]):
			px[x, y] = recolour_pixel(px[x, y], x0 <= x <= x1 and y0 <= y <= y1)
	im.save(dst, optimize=True)


def main():
	os.makedirs(OUT, exist_ok=True)
	for name in ('pokemonshowdownbeta.png', 'pokemonshowdownbeta@2x.png'):
		recolour(os.path.join(PLAY, name), os.path.join(OUT, name))
	print('wrote', os.path.relpath(OUT))


if __name__ == '__main__':
	main()
