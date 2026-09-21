# FireRed — Generation 10 Expansion Foundation

## Decision

Form-change implementation is deferred.

The first modernization phase for FIRERED is structural headroom for Generation 10 and later data. The priority is persistent ID capacity, table indexing, save compatibility, and validation before adding new form-change behavior.

## Reference engine state

Modern-engine reference snapshot:

- repository: `rh-hideout/pokeemerald-expansion`
- reference commit: `75b806a3ab57a81ff1eb6179288981f0b3cc3050`
- FireRed direction: use the modern expansion engine's FRLG path rather than reviving the older standalone `pokefirered-expansion` feature line

Observed persistent Pokémon storage limits in the reference snapshot:

| Field | Current stored width | Encodable range | Current data pressure |
| --- | ---: | ---: | --- |
| species | 11 bits | 0..2047 | species/form IDs already extend beyond 1500 |
| tera type | 5 bits | 0..31 | currently sufficient, but tied to the same packed word |
| held item | 10 bits | 0..1023 | item IDs already extend through 873 |
| move | 11 bits each | 0..2047 | ordinary move IDs currently extend through 847 |
| ability selection | 2-bit slot | 0..3 | stores slot, not the global ability ID |

The immediate hard-risk field is held item: only about 150 numeric IDs remain before the 10-bit ceiling.

Species has more room than items, but forms consume the same namespace and the current 11-bit ceiling is too close for a deliberate Generation 10 foundation.

## Phase 1 capacity target

Do not grow the size of `PokemonSubstruct0`.

Repack its existing 32-bit field budget as:

- species: **12 bits** — IDs 0..4095
- tera type: **6 bits** — IDs 0..63
- held item: **12 bits** — IDs 0..4095
- reserved: **2 bits**

This replaces the current 11/5/10/6 split with 12/6/12/2 while preserving the same 32-bit total.

Target capacities:

| Namespace | Gen10-ready target |
| --- | ---: |
| species/forms | 4096 IDs |
| item IDs | 4096 IDs |
| type IDs | 64 IDs |
| moves | keep current 2048-ID storage in Phase 1 |
| abilities | keep current slot storage; global tables remain independently extensible |

## Why moves are not widened in Phase 1

Each stored move currently uses 11 bits and shares a 16-bit word with evolution-tracking or other packed state.

The ordinary move namespace currently has substantially more headroom than items. Expanding moves immediately would force a second packed-layout redesign and would risk consuming evolution-tracking bits without evidence that Generation 10 requires it.

Therefore:

1. keep the 11-bit stored move ID for the first Gen10-readiness pass;
2. add compile-time and validation alarms before the move namespace approaches the 2047 ceiling;
3. redesign move packing only if a verified future data set requires it.

## Save compatibility

The 12/6/12 layout must **not** simply reinterpret an existing save.

Changing bit widths changes the physical meaning of bits in encrypted Box Pokémon substructures. Existing saves must be handled by an explicit migration path.

Migration requirements:

1. detect the old packed format using a save-format/version marker;
2. decrypt each stored Pokémon using the existing engine path;
3. decode old fields as 11-bit species / 5-bit type / 10-bit held item;
4. rewrite them as 12-bit species / 6-bit type / 12-bit held item;
5. recalculate Pokémon checksums and re-encrypt normally;
6. cover party, PC boxes, daycare and every other persisted Pokémon container;
7. make migration idempotent and mark the save only after all Pokémon are converted successfully;
8. keep IDs unchanged during migration — this is a width migration, not a renumbering pass.

No existing FireRed/Emerald-compatible ID should be remapped merely to obtain extra space.

## Table and code audit required before data import

Before importing Generation 10 content, audit every place that assumes an 8-bit, 10-bit or 11-bit identifier.

At minimum:

- species tables and species-indexed arrays
- Pokédex species mapping
- wild encounter structures
- trainer party structures
- gift/static encounter structures
- daycare and breeding
- evolution tables
- move learnsets
- held-item tables
- bag/PC item storage
- item-script parameters
- shop lists
- pickup tables
- link/trade serialization
- record mixing
- Mystery Gift/Event structures
- save blocks and checksums
- script commands that pass species/item/move IDs
- variables and special-function parameters
- graphics/palette tables indexed by species or item
- debug/test generators

Every boundary must use named count constants and must reject overflow at build or validation time.

## Allocation policy

Generation 10 data must append to the modern canonical namespace. Do not reuse retired IDs and do not insert new values into the middle of existing namespaces unless an upstream canonical source explicitly does so.

Reserve explicit custom ranges only after the official/canonical namespace for that snapshot.

Required rules:

- stable old IDs;
- append-only new official IDs;
- separate custom range;
- machine-readable manifests for every assigned ID;
- no magic numeric literals in gameplay code where a named constant exists.

## Validation gates

A Gen10-ready build is not considered complete until automated checks confirm:

- maximum species ID < 4096;
- maximum item ID < 4096;
- maximum type ID < 64;
- maximum stored move ID < 2048;
- no table truncates IDs to `u8` or an undersized bitfield;
- Pokémon substructure size is unchanged after Phase 1 repacking;
- old-format save migration round-trips known Gen III Pokémon without changing species, held item, moves, personality, IVs, EVs, ribbons or checksum validity;
- new-format saves reload without migration on subsequent boots;
- link/trade code either supports the expanded format explicitly or rejects incompatible peers cleanly.

## Deferred work

The following are intentionally **not Phase 1**:

- runtime form-change mechanics;
- battle-triggered form switching;
- item-triggered form menus;
- species-specific form state machines;
- Generation 10 species/move/item/ability content before official/canonical data is available and verified.

Those features sit on top of this capacity foundation rather than defining it.

## Implementation order

1. Select and pin the executable modern FRLG engine base.
2. Add build-time namespace capacity checks.
3. Implement the 12/6/12/2 Pokémon storage layout.
4. Implement and test old-save migration.
5. Audit every persistent and script-facing ID width.
6. Expand item/species/type tables to the new ceilings.
7. Import verified later-generation data.
8. Return to form-change mechanics only after the storage foundation is stable.
