# Parts note: a clear-lid box under the eave

Nothing here has been tried with this board yet. It is the standard approach
for small outdoor electronics; adjust once you see real photos.

## Parts

| Part | What to look for | Why |
|---|---|---|
| Box | "IP65" or "IP67 junction box with **clear polycarbonate** cover", about 100 × 100 × 70 mm inside | Polycarbonate stays clear in sun and doesn't crack in cold; avoid acrylic (crazes) and polystyrene (yellows, brittle) |
| Desiccant | 2–3 small **indicating silica gel** sachets (they change colour when used up) | Soaks up the moisture sealed in with the board |
| Optional: breather vent | "M12 waterproof breathable vent plug" (ePTFE membrane) | Lets air pressure even out without letting water in, so the seal isn't constantly pumping damp air in and out |
| Black foam | a small piece of self-adhesive black craft foam or a rubber grommet, 3–5 mm thick | A light shield around the lens |
| Mounting | double-sided outdoor foam tape, or two small screws + the board's bracket; stainless screws for the box | |

## Inside the box

- **Lens touching the lid.** Put the camera with its lens right up against the
  clear lid, and put a ring of black foam around the lens between the board
  and the lid. Otherwise the lid reflects the board back into the picture,
  and sunlight bouncing inside the box shows up as haze.
- Clean the lid on both sides before closing it. A fingerprint over the lens is
  a smudge in every photo for months.
- The status LED is switched off in the firmware, so it won't reflect at night.

## Where to put it

- **Under the eave, out of direct rain**, aimed at the tree. The lid facing
  sideways (vertical), not up: water and pollen don't settle on a vertical
  face.
- **Out of the noon sun if you can.** A clear box in full sun gets far hotter
  than the air around it. Lithium batteries age fast above about 45 °C and
  should not go above 60 °C. Shade from the eave helps a lot. A white or light
  box body (clear lid only) helps too.
- Don't point it at the sky or the sun: the camera will expose for the
  bright sky and the tree will come out dark.
- Wifi: walls and the box both cost signal. Before sealing it up, check the
  aiming pictures arrive from the exact spot. The serial monitor shows the
  signal strength (`rssi`); better than -75 is comfortable, worse than -85
  will fail sometimes.

## Condensation

A sealed box traps whatever moisture was in the air when you closed it. On a
cold night the lid is the coldest surface, so that moisture forms dew on the
inside of the lid. That fogs the picture.

What helps, in order of importance:

1. **Close it on a dry day, or close it indoors** where the heating has dried the
   air. Don't close it outside on a humid summer evening.
2. **Silica gel inside**, replaced (or dried in a low oven, per the packet)
   when the colour changes. Check it each time you bring it in to charge.
3. The **photo is at noon by default**, when the lid is warmest and any night
   fog has usually cleared. Morning photo times are the most likely to be
   fogged.
4. Optional breather vent (above).

When you bring it in to charge in winter, **let the closed box warm up to
room temperature before opening it**, or the warm indoor air will condense
on the cold board.

## Cold

- Durham winter nights go below freezing. While the board is switched off
  (23 hours 59 minutes a day) cold does it no harm.
- The battery gives less in the cold and its voltage dips more under the wifi
  bursts. Expect lower `battery_v` readings on cold days and recharge a bit
  sooner in winter.
- **Never charge the battery below 0 °C.** It only charges over USB, so this
  only matters if you charge it outside — don't.
- The ESP32 chip itself is rated well below freezing, but I have not found
  M5Stack's published operating temperature range for the whole Timer Camera X
  board, so cold-weather operation is **unverified**. If winter photos start
  failing on the coldest days, that's the likely reason.

## Charging routine

Every few months, when `battery-log.csv` shows about 3.5 V: bring the box in,
let it reach room temperature, open it, charge over USB for an hour, swap
or dry the silica gel, close it (indoors), put it back. It carries on with
its schedule by itself. If you upload new firmware it re-enters aiming mode,
so re-check the framing.
