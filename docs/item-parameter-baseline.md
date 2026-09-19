# FireRed — Emerald Item Parameter Baseline

## Canonical rule

All item game parameters use Pokémon Emerald as the canonical Generation III
baseline.

The canonical item ID space is the complete Emerald table:

- ITEM_NONE = 0
- shared Ruby/Sapphire/FireRed/LeafGreen/Emerald item IDs retain the Emerald ID
- ITEM_SAPPHIRE = 374
- ITEM_MAGMA_EMBLEM = 375
- ITEM_OLD_SEA_MAP = 376
- ITEMS_COUNT = 377

FireRed already matches Emerald exactly for item IDs 0 through 374. The only
ID-space extension required is Emerald's final two entries, 375 and 376.

## Canonical parameter fields

For every item, compare and normalize against Emerald for:

- item ID and ordering
- item name
- price
- hold effect
- hold-effect parameter
- description semantics
- importance
- registrability
- pocket
- item-use type
- battle-usage class
- secondary ID
- icon and icon palette assignment

Emerald is the source of truth for these fields.

## Runtime-handler compatibility rule

Do not raw-copy an Emerald function pointer when Emerald only disables an
FRLG-specific item because that item is unused in Emerald.

Examples include FireRed/LeafGreen key items such as:

- Bicycle
- Town Map
- VS Seeker
- Fame Checker
- TM Case
- Berry Pouch
- Teachy TV
- Poké Flute

Emerald keeps these IDs and metadata for cross-game compatibility, but several
of their field-use handlers are intentionally CannotUse because their gameplay
systems are absent from Emerald.

For FIRERED, retain the native FireRed runtime handler when it is required for
FireRed gameplay, while keeping the surrounding item identity and parameter
schema aligned with Emerald.

This is a compatibility adapter, not a separate item definition.

## Event items

The event-item order follows Emerald:

1. ITEM_EON_TICKET = 275
2. ITEM_MYSTIC_TICKET = 370
3. ITEM_AURORA_TICKET = 371
4. ITEM_MAGMA_EMBLEM = 375
5. ITEM_OLD_SEA_MAP = 376

The Pallet Town four-choice event menu exposes:

1. Eon Ticket
2. Mystic Ticket
3. Aurora Ticket
4. Old Sea Map

Magma Emblem is retained at ID 375 so Old Sea Map remains the Emerald-canonical
ID 376; it is not one of the four ticket-delivery choices.

## Validation

For every supported FireRed region/revision, validation must confirm:

1. the complete 0..376 item ID table matches the Emerald canonical ordering;
2. every shared item's normalized parameters match the Emerald baseline;
3. FireRed-only gameplay handlers still work where Emerald intentionally uses
   CannotUse;
4. ITEM_MAGMA_EMBLEM and ITEM_OLD_SEA_MAP exist at 375 and 376;
5. icons, palettes, descriptions, save serialization, bag display, give/remove
   item scripts, and link/trade-facing item IDs remain coherent;
6. existing saves do not have their existing 0..374 item IDs remapped.

## Source references

Canonical parameter reference: pret/pokeemerald.
FireRed runtime compatibility reference: pret/pokefirered.

External source trees are technical references only. FIRERED keeps its own
patches, manifests, verification logs, and compatibility decisions.
