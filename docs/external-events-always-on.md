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
- Vermilion ferry access must not require an externally delivered enable flag.
- Altering Cave encounter sets must be selectable/rotatable in-game without Mystery Event transfer.
- Visiting Trainer must use valid local trainer data; never bypass validation against uninitialized save data.

## Behaviour

### Aurora Ticket / Birth Island / Deoxys

- Aurora Ticket can be obtained locally at any time after the normal Mystery Gift/event NPC becomes available.
- Birth Island destination remains permanently available after normal ferry progression permits travel.
- Deoxys encounter remains one-time according to the normal defeated/caught state.

### Mystic Ticket / Navel Rock / Lugia / Ho-Oh

- Mystic Ticket can be obtained locally.
- Navel Rock destination remains permanently available after normal ferry progression permits travel.
- Lugia and Ho-Oh retain their normal one-time encounter flags.

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

Do not globally force every flag to TRUE. Patch the event entry points and their specific gates so unrelated game logic and save semantics remain intact.

Existing saves and new saves must both work. Save normalization must be idempotent.

## Target priority

1. Japanese FireRed v1.0
2. Japanese FireRed v1.1
3. English FireRed v1.0
4. English FireRed v1.1
5. German / French / Italian / Spanish releases

## Source reference

Primary technical reference: pret/pokefirered event scripts, flags, variables, and map scripts. External source trees are reference material only; this repository keeps its own patch/analysis structure.
