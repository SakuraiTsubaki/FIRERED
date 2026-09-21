# FireRed — Generation 10 Expansion Foundation

## Decision

Form-change implementation is deferred.

FIRERED will first expand from the **retail FireRed ROM and save ABI**, verified against the project's actual ROM/SAV inputs. Modern expansion projects remain implementation references, but they do not define the retail FireRed storage limits.

## Evidence baseline

Actual project inputs inspected:

- Japanese FireRed v1.0 / v1.1
- English FireRed v1.0 / v1.1
- German / French / Italian / Spanish FireRed
- matching 128 KiB save files

All eight ROMs are 16 MiB, have valid GBA header checksums, and contain `FLASH1M_V103`.

All inspected saves are 128 KiB and use the retail FireRed layout:

- 32 sectors × 0x1000 bytes
- sector data area: 0xF80 bytes
- two rotating game-save slots
- 14 sectors per game-save slot
- sectors 28–29 reserved for Hall of Fame
- sectors 30–31 reserved for Trainer Tower
- signature: `0x08012025`

The uploaded saves validate with the retail FireRed checksum algorithm and structure sizes.

## Retail persistent Pokémon ABI

The retail FireRed `PokemonSubstruct0` stores:

- species: `u16`
- held item: `u16`
- experience: `u32`

`PokemonSubstruct1` stores all four moves as `u16`.

Therefore retail FireRed already has a 0..65535 persistent ID space for species, held items, and moves. The earlier proposed 11/10/11-bit limits belong to a modern expansion-specific packed format and are **not** adopted as the FIRERED retail baseline.

### Rule

Do not shrink retail 16-bit IDs merely to make room for modern metadata.

Preserve the 80-byte retail Box Pokémon ABI until a separately verified metadata-extension design requires a change.

## Save expansion discovered from actual SAV files

The retail structures do not consume the complete data capacity of their final sectors.

| Structure | Retail size | Allocated sector capacity | Verified zero tail |
| --- | ---: | ---: | ---: |
| SaveBlock2 | 0xF24 | 0xF80 | 0x5C / 92 B |
| SaveBlock1 | 0x3D68 | 0x3E00 | 0x98 / 152 B |
| PokemonStorage | 0x83D0 | 0x8B80 | 0x7B0 / 1968 B |
| **Total** | | | **0x8A4 / 2212 B** |

Every uploaded save has zeros in all three tail regions.

This matters because the retail checksum only sums the structure bytes selected by the save layout. Extending a structure into already-zero tail bytes keeps an old save's checksum numerically unchanged: adding zero words changes neither the sum nor the folded 16-bit checksum.

## Phase 1 save ABI

Reserve the complete verified tail capacity now:

- `SaveBlock2`: append 0x5C bytes
- `SaveBlock1`: append 0x98 bytes
- `PokemonStorage`: append 0x7B0 bytes

The first patch reserves these bytes without assigning speculative form-change semantics.

Benefits:

1. old saves remain loadable without rewriting Pokémon records;
2. future metadata can be subdivided inside a fixed extension ABI;
3. future field additions no longer change save structure size or checksum coverage;
4. Hall of Fame and Trainer Tower sectors remain untouched.

### Compatibility rule

On a legacy save, all extension bytes are zero and represent extension version 0 / uninitialized state.

When later features allocate fields inside the reserved regions, initialization must be explicit and idempotent. Existing retail IDs must never be renumbered as part of extension initialization.

## ROM expansion — maximum standard GBA profile

The inspected retail ROMs are 16 MiB.

For the FIRERED expanded profile, use the **maximum standard directly-addressable GBA ROM size: 32 MiB**.

- physical/direct ROM image: `0x02000000` bytes = **32 MiB**
- primary Game Pak window: `0x08000000 .. 0x09FFFFFF`
- build end / pad-to address: `0x0A000000`
- linker region: `ROM (rx) : ORIGIN = 0x08000000, LENGTH = 32M`

The GBA also exposes ROM at `0x0A000000 .. 0x0BFFFFFF` and `0x0C000000 .. 0x0DFFFFFF`, but these are alternate wait-state images of the **same cartridge ROM**, not independent extra 32 MiB banks. They must not be counted as 64 or 96 MiB of ordinary directly-addressable cartridge storage.

Therefore the standard-hardware FIRERED ceiling is fixed at **32 MiB**.

Going above 32 MiB is explicitly out of the standard profile because it requires cartridge-specific mapping/bank switching or emulator/flashcart-specific behavior. If such a profile is ever added, it must be separate and must never silently replace the hardware-compatible 32 MiB profile.

Retail free/padding runs remain evidence and comparison data, not the allocator of record. New data must be linker-controlled.

## What actually needs a width audit

Because Pokémon/item/move IDs are already 16-bit in persistent Pokémon data, the Gen10 audit must focus on **other** narrowing boundaries:

- `u8` species/item/move parameters in tables or scripts
- Pokédex indexing and bitfield sizes
- bag, PC, shop and pickup structures
- trainer party encodings
- wild/static/gift encounter encodings
- evolution and learnset encodings
- ability-slot storage
- Poké Ball storage
- met-game / met-location storage
- ribbons and later-generation persistent metadata
- link/trade packet formats
- Mystery Gift/Event records
- save-block fixed arrays
- graphics/palette table indexing
- script variables and special-function arguments

Every discovered narrowing point must be documented before it is widened.

## Form-change status

Deferred.

No runtime form-switch system, form menu, battle-triggered transformation, or species-specific form state machine belongs in Phase 1. The storage and ROM-capacity foundation comes first.

## Implementation order

1. Keep the verified ROM/SAV evidence manifest in FIRERED.
2. Keep an analyzer that reproduces ROM-header and save-sector verification.
3. Reserve the verified 2212-byte save tail as a stable extension ABI.
4. Build the FIRERED expanded profile at the **32 MiB standard GBA maximum**.
5. Audit all narrowing ID/metadata boundaries.
6. Add modern persistent metadata deliberately, with compatibility tests.
7. Import verified later-generation data.
8. Return to form-change mechanics after the foundation is stable.
