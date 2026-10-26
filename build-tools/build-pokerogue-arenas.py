#!/usr/bin/env python3
"""Battle backdrops and page backgrounds from PokéRogue's biome art.

    python3 build-tools/build-pokerogue-arenas.py <pokerogue-assets>/images/arenas

Writes play.pokemonshowdown.com/sprites-custom/arenas/<biome>.png (700x500 battle
backdrops), sprites-custom/backgrounds/<biome>.png (1920x1080 page backgrounds), and
sprites-custom/backgrounds/pokerogue.png (the default page background: the End's
scenery without its bases).
Needs Pillow. The art is CC BY-NC-SA 4.0: see sprites-custom/README.md for credits.

A Showdown backdrop is 700x500 and the visible battle frame is the 640x360 area
at (50,90). Each backdrop is:
  - the 320x180 biome background at 2x (nearest neighbour), filling the frame
  - the enemy base and its scenery props at 2.5x, placed under the far Pokémon
  - the base again at 3.5x under the near Pokémon (PokéRogue hides most of its
    player base behind the message box, so that one is never whole)
  The bases are bigger than PokéRogue's because Showdown spreads its Pokémon
  wider, especially in doubles.
  - the 50/90 px margins repeat the frame's outer edge, for when the frame shakes

Where Showdown stands Pokémon (pos() and recalculatePos() in
src/battle-animations.ts; "feet" = the bottom of the sprite):
  far  side: x 430 (doubles 448 / 348-373), feet at y 155-192
  near side: x 210 (doubles 174-183 / 295-374), feet at y 282-333
With the numbers below, the feet of 93-100% of Pokémon land on the bases in
every singles and doubles slot, with both the BW and the 3D sprites (the misses
are mostly fliers and Gigantamax forms, which hover over or tower past any base).
"""
import json
import os
import sys

from PIL import Image

BIOMES = [
	'abyss', 'badlands', 'beach', 'cave', 'construction_site', 'desert', 'dojo', 'end',
	'factory', 'fairy_cave', 'forest', 'grass', 'graveyard', 'ice_cave', 'island', 'jungle',
	'laboratory', 'lake', 'meadow', 'metropolis', 'mountain', 'plains', 'power_plant',
	'rockycoast', 'ruins', 'sea', 'seabed', 'slum', 'snowy_forest', 'space', 'swamp',
	'tall_grass', 'temple', 'town', 'volcano', 'wasteland', 'well',
]

# in battle-frame pixels (640x360): the scale of each base, and where its middle goes
FAR_SCALE = 2.5
FAR_CENTRE = (430, 172)
NEAR_SCALE = 3.5
NEAR_CENTRE = (260, 318)
# Every biome's enemy base is drawn on the same 128x32 ellipse at (152,58) of its
# 320x132 canvas (some have grass or signs sticking out), so this is its middle
BASE_MIDDLE = (216, 74)
PAGE_SCALE = 6
# The client's default page background (backgrounds/pokerogue.png): just this
# biome's scenery, with no base or props, so it doesn't look like a battlefield
DEFAULT_PAGE_BIOME = 'end'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play.pokemonshowdown.com', 'sprites-custom')


def load(arenas, name):
	path = os.path.join(arenas, name + '.png')
	if not os.path.exists(path):
		return None
	return Image.open(path).convert('RGBA')


def first_frame(arenas, name):
	"""The first frame of an animated base (the End's), on its 320x132 canvas."""
	sheet = load(arenas, name)
	with open(os.path.join(arenas, name + '.json')) as f:
		data = json.load(f)
	frame = data['textures'][0]['frames'][0]
	box, src = frame['frame'], frame['spriteSourceSize']
	out = Image.new('RGBA', (frame['sourceSize']['w'], frame['sourceSize']['h']))
	out.alpha_composite(sheet.crop((box['x'], box['y'], box['x'] + box['w'], box['y'] + box['h'])), (src['x'], src['y']))
	return out


def layers(arenas, biome):
	"""background, enemy base, and the scenery props PokéRogue scatters around it"""
	if biome == 'end':
		base = first_frame(arenas, 'end_b')
		props = [load(arenas, 'end_b_1'), load(arenas, 'end_b_2')]
	else:
		base = load(arenas, biome + '_b')
		props = [load(arenas, biome + p) for p in ('_b_1', '_b_2', '_b_3')]
	return load(arenas, biome + '_bg'), base, [p for p in props if p and p.size == base.size]


def scaled(im, n):
	return im.resize((round(im.size[0] * n), round(im.size[1] * n)), Image.NEAREST)


def battle_frame(arenas, biome):
	bg, base, props = layers(arenas, biome)
	frame = scaled(bg, 2)
	mx, my = BASE_MIDDLE
	field = base.copy()
	for prop in props:
		field.alpha_composite(prop)  # PokéRogue draws props in front of the base
	frame.alpha_composite(
		scaled(field, FAR_SCALE),
		(round(FAR_CENTRE[0] - mx * FAR_SCALE), round(FAR_CENTRE[1] - my * FAR_SCALE)))
	box = base.getchannel('A').getbbox()
	near = scaled(base.crop(box), NEAR_SCALE)
	frame.alpha_composite(
		near,
		(round(NEAR_CENTRE[0] - (mx - box[0]) * NEAR_SCALE), round(NEAR_CENTRE[1] - (my - box[1]) * NEAR_SCALE)))
	return frame


def page_background(arenas, biome):
	"""The biome with the enemy base and props, blown up 6x (1920x1080) so browsers
	don't blur the pixel art much when they stretch it over the page"""
	bg, base, props = layers(arenas, biome)
	out = bg.copy()
	field = base.copy()
	for prop in props:
		field.alpha_composite(prop)
	out.alpha_composite(field)
	return scaled(out, PAGE_SCALE)


def default_page_background(arenas):
	"""The default biome's scenery on its own: no bases, and none of the props that
	stand on them"""
	return scaled(layers(arenas, DEFAULT_PAGE_BIOME)[0].convert('RGB'), PAGE_SCALE)


def backdrop(frame):
	frame = frame.convert('RGB')
	out = Image.new('RGB', (700, 500))
	out.paste(frame, (50, 90))
	out.paste(frame.crop((0, 0, 640, 1)).resize((640, 90)), (50, 0))
	out.paste(frame.crop((0, 359, 640, 360)).resize((640, 50)), (50, 450))
	out.paste(out.crop((50, 0, 51, 500)).resize((50, 500)), (0, 0))
	out.paste(out.crop((689, 0, 690, 500)).resize((10, 500)), (690, 0))
	return out


def main():
	arenas = sys.argv[1]
	out = sys.argv[2] if len(sys.argv) > 2 else OUT
	os.makedirs(os.path.join(out, 'arenas'), exist_ok=True)
	os.makedirs(os.path.join(out, 'backgrounds'), exist_ok=True)
	for biome in BIOMES:
		name = biome.replace('_', '')
		backdrop(battle_frame(arenas, biome)).save(os.path.join(out, 'arenas', name + '.png'), optimize=True)
		page_background(arenas, biome).convert('RGB').save(os.path.join(out, 'backgrounds', name + '.png'), optimize=True)
	default_page_background(arenas).save(os.path.join(out, 'backgrounds', 'pokerogue.png'), optimize=True)
	print(f'{len(BIOMES)} biomes and the default background written to {out}')


if __name__ == '__main__':
	main()
