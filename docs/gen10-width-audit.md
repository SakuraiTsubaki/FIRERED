# FireRed Generation-10 Width Audit

Reference source: `pret/pokefirered@c75f352304d529f6ba92d4f74b9cf8b5c3810788`.

Form-change mechanics remain deferred. This document tracks the structural work completed before later-generation data import.

## Build-verified foundation

The complete patch stack `0004..0015` applies cleanly to the pinned FireRed source and passes the `Gen10 Expansion` GitHub Actions workflow, including a full **32 MiB** `pokefirered_modern.gba` build.

### Already wide enough in retail FireRed

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

## Implemented patches

### 0004 — retail save extension ABI

Reserves the verified zero-filled retail save tails without changing the flash-sector map:

- SaveBlock2: 92 bytes
- SaveBlock1: 152 bytes
- PokemonStorage: 1968 bytes
- total: 2212 bytes

Legacy saves remain compatible because the supplied retail saves contain zero in every reserved tail byte.

### 0005 — 32 MiB standard GBA ROM profile

The expanded build pads to `0x0A000000`, producing a 33,554,432-byte ROM while keeping the retail profile separate.

### 0006 — full 16-bit level-up move IDs

Retail level-up entries pack move IDs into 9 bits. The expanded format stores `move:u16, level:u16` and raises the helper ceiling to 64 logical entries.

### 0007 / 0008 / 0013 — 4096-species Pokédex storage

PokemonStorage contains:

- Seen: 512 bytes
- Caught: 512 bytes
- capacity: 4096 National Dex IDs

Retail IDs 1..386 continue using the original anti-cheat arrays and mirror SET operations into the extension. IDs above the retail National Dex boundary use the extension bitsets. Patch 0013 freezes the original 52-byte retail arrays so increasing `NUM_SPECIES` cannot move later save fields.

### 0009 / 0011 / 0012 — 16-bit abilities and three slots

Build-verified ability foundation:

- global ability ID: `u16`
- species ability slots: 3
- normal Box Pokémon ability slot: 2 bits via extension metadata
- Battle Tower auxiliary Pokémon: 2-bit slot while preserving the retail serialized bit
- battle history/message paths: 16-bit ability IDs
- switch-prevention controller packet: 16-bit ability ID without increasing its existing 8-byte transfer
- `jumpifability` and `jumpifabilitypresent`: 16-bit battle-script operands

### 0010 — compatible per-Pokémon metadata word

The retail 80-byte `BoxPokemon` size is preserved. The former `unknown` / `MON_DATA_ENCRYPT_SEPARATOR` header word becomes `extensionData`.

Currently wired:

- ability slot high bit
- Poké Ball high bits

The remaining bits stay reserved until a later metadata design is verified.

### 0014 — frozen legacy Unown IDs

Retail Egg and Unown form-only IDs are frozen:

- Egg: 412
- Unown B..? : 413..439
- first safe expanded regular species ID: 440

This prevents legacy form graphics IDs from moving when later generations are appended.

### 0015 — 64-ID battle Poké Ball accounting

The Box Pokémon format already supports 6-bit / 64-value Poké Ball storage after 0010. Battle runtime now matches that ceiling:

- authoritative caught-ball runtime ID: byte-sized field
- catch-attempt counters: 64 entries
- attempt indexing uses `ItemIdToBallId()`, not `gLastUsedItem - ITEM_ULTRA_BALL`

This removes the retail contiguous-item-ID assumption before later-generation balls are imported.

## ROM/SAV evidence revalidated

The eight supplied FireRed ROMs and eight supplied SAV files were re-read on 2026-09-29.

ROMs:

- Japanese v1.0 / v1.1
- English v1.0 / v1.1
- German / French / Italian / Spanish

All eight ROM SHA-256 values match `manifests/rom-save-evidence.json`, all are 16 MiB, all GBA header checksums validate, and all contain `FLASH1M_V103`.

All eight saves match the manifest hashes and retail 128 KiB layout. Their observed normal save sectors pass the FireRed checksum algorithm, and all verified unused tail bytes remain zero. Japanese v1.1 has one valid 14-sector slot; the other supplied saves contain two valid rotating slots.

## Remaining structural work

The next audited targets are:

- Pokédex UI/list and later-generation species-to-National-Dex mapping
- actual later-generation Poké Ball item -> ball ID mappings, graphics and catch behavior
- bag Poké Ball pocket capacity / overflow design
- `metGame:4`
- `metLocation:u8`
- ribbons and other modern persistent per-Pokémon metadata
- remaining link/trade packet assumptions
- remaining script byte-sized semantic IDs
- trainer class / graphics ID widths
- map group / map number widths

The rule remains: do not widen every byte mechanically. Widen a field only when its semantic namespace requires it, and keep save/link compatibility explicit.

## Next implementation order

1. prepare expanded species/National Dex mapping without moving retail save fields;
2. design later-generation Poké Ball catalog + bag capacity together;
3. widen origin-game/location metadata with an 80-byte Box Pokémon-compatible design;
4. complete link/trade and script-width audit;
5. begin verified later-generation species/move/ability/item data import;
6. return to form-change mechanics only after the foundation remains build-clean.
