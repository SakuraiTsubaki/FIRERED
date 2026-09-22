# FireRed Generation-10 Width Audit

Reference source: `pret/pokefirered@c75f352304d529f6ba92d4f74b9cf8b5c3810788`.

This audit separates fields that are already future-safe from fields that must be widened before later-generation data is imported. Form-change mechanics are intentionally excluded.

## Already wide enough

The following retail FireRed paths already use 16-bit identifiers and do not need artificial repacking:

| Domain | Retail representation | Status |
| --- | --- | --- |
| Box Pokémon species | `u16` | ready |
| Box Pokémon held item | `u16` | ready |
| Box Pokémon moves | `u16[4]` | ready |
| trainer species | `u16` | ready |
| trainer held item | `u16` | ready |
| trainer custom moves | `u16[4]` | ready |
| wild encounter species | `u16` | ready |
| bag/PC ItemSlot item ID | `u16` | ready |
| roamer species | `u16` | ready |
| Mail species/item | `u16` | ready |
| Wonder Card icon species | `u16` | ready |

The target namespace policy for species, items and moves remains 16-bit.

## Confirmed blockers

### Level-up learnsets

Retail encoding uses one `u16` with 9 move bits and 7 level bits:

- move ceiling: 511
- level ceiling: 127
- helper ceiling: `MAX_LEVEL_UP_MOVES = 20`

This is already too narrow for post-Generation-III move IDs.

Resolution: `patches/0006-wide-levelup-learnsets.patch`.

Expanded representation uses two `u16` words per entry: `move, level`, with 64 logical entries per species.

### Global ability IDs

Retail structures use `u8` ability IDs in multiple runtime and text/battle paths:

- `SpeciesInfo.abilities[2]`
- `BattlePokemon.ability`
- `gLastUsedAbility`
- `BattleMsgData.lastAbility`
- `BattleMsgData.abilities[]`
- battle history / text buffers

The modern reference already exceeds 255 abilities, so this is a present blocker, not merely a Generation-10 prediction.

Required target:

- global ability ID: at least `u16`
- species ability slots: 3
- active ability slot: at least 2 bits
- battle text serialization must carry 16-bit ability IDs

This change touches battle/link buffer ABI and will be implemented as a coordinated patch rather than a one-field type edit.

### Ability slot persistence

Retail `BoxPokemon` stores `abilityNum:1`, allowing only two slots.

The retail 80-byte Box Pokémon ABI is deliberately preserved for now. Do not consume undocumented bits merely because they look unused. Hidden-ability persistence needs a verified sidecar or migration design.

### Poké Ball persistence

Retail Box Pokémon stores `pokeball:4`, allowing only 16 encoded values. Later-generation balls require a wider persistent representation.

This is another per-mon metadata problem and belongs with the same sidecar/migration design as hidden ability state.

### Pokédex capacity

Retail Pokédex seen/caught arrays are Generation-III-sized.

The verified PokemonStorage tail is now assigned a 4096-species extended namespace:

- extended seen: 512 bytes
- extended caught: 512 bytes
- remaining PokemonStorage extension reserve: 944 bytes

See `patches/0007-gen10-save-schema.patch`.

Native Pokédex accessors still need to be bridged to the extended bitsets before species above the retail Dex range are considered supported.

## Fields to keep under audit

These are not immediate ID failures but have fixed-width semantics that later systems may outgrow:

- `metLocation: u8`
- `metGame:4`
- `pokeball:4`
- ribbon bitfields
- `BattleResults.caughtMonBall:4`
- Battle Controller / link packet layouts
- script byte arguments
- trainer class / graphics IDs
- map group / map number fields

The rule is not “widen every u8”. Widen only fields whose semantic namespace requires it, and keep protocol/save changes explicit.

## Order

1. full-u16 level-up moves;
2. typed 4096-species save/Dex reserve;
3. coordinated 16-bit ability runtime and battle-message ABI;
4. hidden-ability + Poké Ball persistent metadata;
5. extended Pokédex accessor integration;
6. remaining script/link/protocol width audit;
7. later-generation data import;
8. form changes after the foundation is stable.
