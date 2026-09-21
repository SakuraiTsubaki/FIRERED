# FireRed ROM/SAV Expansion Baseline

This record is derived from the FireRed ROM and save files supplied to the project. The binaries themselves are not stored in GitHub.

## ROM observations

All inspected ROMs are exactly 16 MiB and have valid GBA header checksums.

| Region | Game code | Revision |
| --- | --- | ---: |
| Japan | BPRJ | 0 |
| Japan | BPRJ | 1 |
| English | BPRE | 0 |
| English | BPRE | 1 |
| Germany | BPRD | 0 |
| France | BPRF | 0 |
| Italy | BPRI | 0 |
| Spain | BPRS | 0 |

Every inspected ROM contains `FLASH1M_V103`, matching the 128 KiB save files.

The ROMs contain substantial 0xFF padding/free runs, but FIRERED will not treat retail padding offsets as a stable allocator. The long-term source build target should use linker-controlled ROM expansion instead.

## SAV observations

Every save is 128 KiB = 32 × 4 KiB flash sectors.

The retail source layout was tested directly against the input saves:

- sector data = 0xF80 bytes
- footer = 0x80 bytes
- 14 sectors per normal save slot
- 2 normal save slots
- sectors 28–29 = Hall of Fame
- sectors 30–31 = Trainer Tower
- signature = `0x08012025`

All observed normal sectors with that signature pass the retail FireRed checksum algorithm.

The Japanese v1.1 sample currently contains one valid 14-sector save slot; the other supplied samples contain two valid rotating slots. This is valid retail behavior and is not a format difference.

## Verified extension capacity

The final chunk of each retail save structure ends before the end of its allocated sector range:

| Structure | Size | Capacity | Tail |
| --- | ---: | ---: | ---: |
| SaveBlock2 | 0xF24 | 0xF80 | 0x5C |
| SaveBlock1 | 0x3D68 | 0x3E00 | 0x98 |
| PokemonStorage | 0x83D0 | 0x8B80 | 0x7B0 |

All three tails are entirely zero in every supplied save.

Because normal saving clears the whole sector buffer before copying structure data, retail saves write zero into these unused tail regions. Extending the checksum-covered structure length over those zeros preserves the numerical checksum of legacy saves.

Therefore FIRERED can reserve **0x8A4 = 2212 bytes** without changing the flash-sector map and without consuming Hall of Fame / Trainer Tower sectors.

## Persistent ID width

Retail FireRed does **not** store species/item/move IDs in 10- or 11-bit fields:

- `species`: u16
- `heldItem`: u16
- each move: u16

The persistent ID namespace is already 16-bit. The Gen10 foundation should preserve this retail property and audit narrower tables/commands individually instead of shrinking these fields.

## Reproduction

Run:

```sh
python tools/analyze_fire_red_inputs.py path/to/*.gba path/to/*.sav -o report.json
```

Compare the result with `manifests/rom-save-evidence.json`.
