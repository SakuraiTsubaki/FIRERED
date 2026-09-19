# FireRed — External Events Always-On

## Goal

Remove dependence on external distribution hardware, Wonder Cards, e-Reader data transfer, or limited-time event delivery for event content already present in Pokémon FireRed.

"Always-on" means the event remains permanently available in normal gameplay. One-time rewards remain one-time unless explicitly designed otherwise. Normal story/progression gates are preserved; only the external-distribution dependency is removed.

## Scope

### Mystery Event scripts embedded in FireRed

1. Stamp Card
2. Surf Pichu
3. Visiting Trainer / e-Reader trainer
4. Battle Card
5. Aurora Ticket
6. Mystic Ticket
7. Altering Cave

### Required gate changes

- Mystery Gift deliveryman must no longer disappear just because no valid Wonder Card is stored.
- Aurora Ticket / Birth Island must not depend on external Wonder Card delivery.
- Mystic Ticket / Navel Rock must not depend on external Wonder Card delivery.
- Vermilion ferry access for Navel Rock and Birth Island must depend on the ticket item only, not `FLAG_ENABLE_SHIP_*`.
- Altering Cave encounter sets must be selectable/rotatable in-game without Mystery Event transfer.
- Visiting Trainer must use valid local trainer data; never bypass validation against uninitialized save data.

## Behaviour

### Ticket rule

The ticket itself is the entitlement.

Ticket distribution is moved in-game: a dedicated Mystery Gift deliveryman is permanently placed in Pallet Town from the beginning of the game. No external Mystery Gift data is required.

Talking to the NPC opens exactly four event-item choices:

1. Eon Ticket
2. Aurora Ticket
3. Mystic Ticket
4. Old Sea Map

Pressing B cancels the menu.

- `ITEM_EON_TICKET` already exists in FireRed's item table, but Southern Island gameplay does not; Southern Island/Latios-Latias event support must be ported before the ticket has a destination.
- `ITEM_AURORA_TICKET` alone enables Birth Island in the Vermilion ferry destination logic.
- `ITEM_MYSTIC_TICKET` alone enables Navel Rock in the Vermilion ferry destination logic.
- Do not require `FLAG_ENABLE_SHIP_BIRTH_ISLAND` or `FLAG_ENABLE_SHIP_NAVEL_ROCK`.
- The Pallet Town deliveryman is visible from the start and never disappears.
- Choosing a ticket already owned does not create a duplicate.
- If a ticket is later absent from the bag, the player can choose it again.
- FireRed does not define `ITEM_OLD_SEA_MAP`; Old Sea Map item data/icon and Faraway Island/Mew event logic must be ported from Emerald rather than assigning a fake item ID.
- `FLAG_RECEIVED_AURORA_TICKET` and `FLAG_RECEIVED_MYSTIC_TICKET` are not required for access.
- `FLAG_SHOWN_AURORA_TICKET` and `FLAG_SHOWN_MYSTIC_TICKET` may remain because they only control the one-time ferry explanation.
- Legendary encounter completion flags remain unchanged.

This makes old and new saves behave consistently: possession of the Key Item is the single source of truth.

### Eon Ticket / Southern Island / Latios-Latias

- Eon Ticket is selectable from the Pallet Town deliveryman.
- FireRed already contains `ITEM_EON_TICKET`, including item/icon references.
- Southern Island and its encounter/event state are not native FireRed content and must be ported before Eon Ticket is considered fully functional.

### Aurora Ticket / Birth Island / Deoxys

- Aurora Ticket can be selected from the Pallet Town deliveryman.
- Birth Island becomes a destination whenever the player has the Aurora Ticket and has reached the normal Seagallop ferry progression.
- Deoxys remains a one-time encounter according to the original battle/event state.

### Mystic Ticket / Navel Rock / Lugia / Ho-Oh

- Mystic Ticket can be selected from the Pallet Town deliveryman.
- Navel Rock becomes a destination whenever the player has the Mystic Ticket and has reached the normal Seagallop ferry progression.
- Lugia and Ho-Oh retain their original one-time encounter flags.

### Old Sea Map / Faraway Island / Mew

- Old Sea Map is one of the four Pallet Town choices.
- FireRed contains a reserved `FLAG_RECEIVED_OLD_SEA_MAP` entry, explicitly noted in source as unused until Emerald, but does not define the Old Sea Map item itself.
- Port the Emerald Old Sea Map key item, icon/palette, Faraway Island maps, ferry routing, Mew encounter behavior, and one-time completion state as one coherent feature.
- Do not expose the choice as a fake/no-op final implementation.

### Altering Cave

- Remove the need for a downloaded Mystery Event to increment `VAR_ALTERING_CAVE_WILD_SET`.
- Provide an in-game selector/cycler for every valid Altering Cave encounter table.
- Never depend on RTC.

### Surf Pichu

- Make the embedded Surf Pichu Egg event locally claimable.
- Preserve the existing one-claim semantics and party-space check.

### Stamp Card / Battle Card

- Make the embedded card functionality accessible locally.
- Preserve card/stat semantics instead of faking completion flags.

### Visiting Trainer / e-Reader

- Make visiting-trainer content usable without physical e-Reader / wireless distribution.
- Bundle or generate valid trainer records from documented official data.
- Do not simply force `ValidateEReaderTrainer` to succeed on empty or invalid save data.

## Implementation rule

Do not globally force every flag to TRUE. Patch the specific external-distribution gates so unrelated game logic and save semantics remain intact.

For ticket islands specifically, the Key Item is authoritative. Do not synchronize or repair obsolete enable/received flags just to make ferry access work.

Existing saves and new saves must both work. Save normalization must be idempotent.

## Target priority

1. Japanese FireRed v1.0
2. Japanese FireRed v1.1
3. English FireRed v1.0
4. English FireRed v1.1
5. German / French / Italian / Spanish releases

## Source reference

Primary technical reference: pret/pokefirered event scripts, flags, variables, and map scripts. External source trees are reference material only; this repository keeps its own patch/analysis structure.
