# Custom sprites

Images this client shows instead of Showdown's own.

- `items/maxmushrooms.png`: Max Mushrooms, from [PokéRogue](https://pokerogue.net)
  ([pokerogue-assets](https://github.com/pagefaultgames/pokerogue-assets), `images/items/max_mushrooms.png`),
  resized to Showdown's 24×24 item icons. All rights stay with its original creators.

Item icons are listed in `CUSTOM_ITEM_ICONS` in `src/battle-dex.ts`.

## PokéRogue biomes

- `arenas/<biome>.png`: battle backdrops (700×500, shown in Gen 6+ battles; see `PokeRogueArenas` in
  `src/battle-animations.ts`)
- `backgrounds/<biome>.png`: page backgrounds (1920×1080; the background picker's "PokéRogue biomes",
  and the default; see `Storage.bg.POKEROGUE` in `src/oldclient/storage.js`)

Both are made from the biome art of [PokéRogue](https://pokerogue.net)
([pokerogue-assets](https://github.com/pagefaultgames/pokerogue-assets), `images/arenas/`) by
`build-tools/build-pokerogue-arenas.py`. **Changes:** each biome's background, base and scenery layers
were combined, the bases were moved and enlarged so they sit under Showdown's Pokémon (with a second
base added on the near side), and everything was upscaled with nearest-neighbour scaling.

**Artists** ([PokéRogue's credits](https://github.com/pagefaultgames/pokerogue/blob/beta/CREDITS.md)):

- Backgrounds by **Squip** (paid commissions), with contributions by **Someonealive-QN** and
  **redactedinlight**
- Rocky Coast and Well by **Vari**

© Pagefault Games and the artists above. Licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (non-commercial use, share
alike), and these edited versions are shared under the same licence. The PokéRogue logo is not
used anywhere here: Pagefault Games doesn't allow it to be reused.
