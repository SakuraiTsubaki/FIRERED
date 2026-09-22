# FireRed Generation-10 Width Audit

Reference source: `pret/pokefirered@c75f352304d529f6ba92d4f74b9cf8b5c3810788`.

Form-change mechanics remain deferred. This document tracks the structural work needed before later-generation data is imported.

## Retail paths already wide enough

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

Species, item and move namespace policy remains 16-bit.

## Gen10 foundation patches

### Level-up learnsets — patch 0006

Retail encoding packs a move and level into one `u16`:

- move: 9 bits, ceiling 511
- level: 7 bits
- helper ceiling: 20 entries

`patches/0006-wide-levelup-learnsets.patch` changes the expanded profile to two `u16` words per logical entry: `move, level`, and raises the helper ceiling to 64 logical entries.

Resulting target:

- level-up move ID: 0..65535
- level storage: u16
- save ABI: unchanged
- cost: ROM table growth, intentionally paid from the 32 MiB ROM profile

### Save / Pokédex schema — patches 0007 and 0008

The verified retail save tails are assigned a fixed typed ABI without increasing the flash-sector map.

PokemonStorage allocates:

- 4096-species Seen bitset: 512 bytes
- 4096-species Caught bitset: 512 bytes
- remaining PokemonStorage extension reserve: 944 bytes

`patches/0008-extended-dex-flags.patch` bridges flag access:

- retail National Dex range keeps the original FireRed anti-cheat Seen/Caught fields;
- native SET operations mirror into the extension bitsets;
- IDs above the retail National Dex range use the extension bitsets directly, up to 4096.

Pokédex UI lists and later-generation species-to-National-Dex mappings remain a later data-import task.

### Global ability IDs — patch 0009

Retail FireRed uses `u8` global ability IDs in species, battle, AI and message paths. The modern reference already exceeds ID 255.

`patches/0009-wide-ability-ids.patch` targets:

- global ability IDs: `u16`
- species ability table: three slots
- battle ability value: `u16`
- battle history / message values: `u16`
- switch-prevention ability packet: 16-bit

The existing `CONTROLLER_CHOOSEPOKEMON` packet already transfers 8 bytes while retail initializes only 7. The expanded profile uses byte 7 as the high ability byte, so that controller packet does not grow.

### Per-Pokémon modern metadata — patch 0010

Retail `BoxPokemon` has an existing 16-bit header word named `unknown` / exposed through `MON_DATA_ENCRYPT_SEPARATOR`.

Source inspection shows:

- it is outside the encrypted 48-byte Pokémon substructures;
- `CalculateBoxMonChecksum` sums only the four encrypted substructures, not this header word;
- it has no normal gameplay read semantics in retail FireRed;
- normal whole-`BoxPokemon` copies carry it with the Pokémon.

The expanded profile reuses this word as `extensionData` while preserving the exact 80-byte Box Pokémon size.

Bit allocation:

| Bits | Use |
| --- | --- |
| 0 | ability-slot high bit |
| 1..2 | Poké Ball high bits |
| 3..8 | reserved 6-bit modern type metadata |
| 9 | reserved modern boolean metadata |
| 10..15 | reserved six per-stat metadata bits |

Together with the original low bits this gives:

- ability slot: 2 bits / 0..3; slots 0, 1, 2 usable and slot 3 reserved
- Poké Ball: 6 bits / 0..63

The battle-only `isEgg` bit was only being assigned and not consumed in the inspected retail battle paths, so the runtime `BattlePokemon` bit is reassigned to make `abilityNum` two bits without growing `BattlePokemon`.

## Remaining blockers / audits

These still need work before the foundation can be considered complete:

- Battle Tower / e-Reader auxiliary Pokémon format still has a one-bit `abilityNum`
- `BattleResults.caughtMonBall:4` still needs a wider runtime/result representation
- Pokédex UI and mapping tables still cover only the retail species set
- `metLocation: u8`
- `metGame:4`
- ribbon / later-generation persistent metadata
- remaining Battle Controller and link packet assumptions
- script byte arguments
- trainer class / graphics IDs
- map group / map number fields

The rule is not “widen every u8”. Widen only fields whose semantic namespace needs it, and keep every protocol/save compatibility change explicit.

## Validation gate

The foundation patch stack `0004..0010` is applied to the pinned FireRed source and built by `.github/workflows/gen10-expansion.yml`.

Do not mark a source change as build-verified until that workflow completes successfully.

## Next order

1. make `0004..0010` apply/build clean in CI;
2. widen Battle Tower auxiliary ability persistence safely;
3. widen remaining Poké Ball result paths;
4. complete extended Pokédex mapping/UI foundation;
5. audit scripts/link protocols;
6. import verified later-generation data;
7. return to form changes only after the structural foundation is stable.
