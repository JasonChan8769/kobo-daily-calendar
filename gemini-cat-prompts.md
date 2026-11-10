# Gemini prompts: your own cat on the calendar

Use the Gemini app (Create image / Nano Banana). Fill in the [BRACKETS] about your cat.

## Before you start

- **Photos:** 3-5 clear photos of your cat in good light: face straight-on, side profile, full body, plus a close-up of any special markings.
- **One chat for the whole character.** Upload the photos in the first message, and keep every later pose in the same chat so the face and coat stay consistent. (Or save it as a Gem.)
- **No transparent PNG from Gemini.** So every prompt asks for a pure white background and a closed dark outline. I remove the white with a script afterwards, and the outline keeps white fur from being cut away.
- **No text inside the picture.** All text on the calendar is drawn by code.
- Generate 3-4 variations of each prompt and keep the best one.

## 1. Style block (paste at the end of EVERY prompt)

```
STYLE: flat 2D illustration in the spirit of a vintage Hong Kong / Japanese
printed wall-calendar. Clean, confident dark-brown outline of even thickness
(thick enough to stay clear when the image is shrunk to 700px tall). Solid flat
colour fills only: no gradients, no soft shadows, no fur texture, no halftone,
no glow, no sparkles. Keep my cat's real fur colours but make them bold and
saturated. Use deep indigo blue and vivid pure red for clothes and accessories,
plus warm cream and dark brown for details. Cute, slightly dignified proportions
(big head, small body), expressive eyes. Whole body visible, centred, nothing
cropped, 3:4 portrait. Pure solid white background (#FFFFFF), no ground shadow,
no floating objects, no border, no text, no logo, no watermark.
```

## 2. Step one: character sheet (do this first)

```
Here are photos of my cat. Create a character design sheet of THIS exact cat:
[COAT: e.g. orange tabby with a white chest and white paws], [EYES: e.g. amber
eyes], [MARKINGS: e.g. a small dark spot on the left cheek], [BUILD: e.g. round
and chubby]. Show 3 views on one sheet: front, three-quarter and sitting.
Keep the face, coat pattern, eye colour and body shape faithful to the photos,
simplified into the illustration style below. Dress the cat in a small red
scarf as a recurring costume detail.
[PASTE STYLE BLOCK]
```

Pick the version that looks most like your cat. Everything else builds on it.

## 3. Step two: the main calendar pose

```
Using the character sheet we just made (same face, same coat, same proportions,
same red scarf), draw the cat standing on two legs, one paw raised in a friendly
wave, looking at the viewer. Leave empty space on its left side.
[PASTE STYLE BLOCK]
```

## 4. Pose library (use the same pattern for each)

```
Using the same cat as the character sheet (identical face, coat and proportions),
new pose: [POSE FROM THE TABLE]. [PASTE STYLE BLOCK]
```

| Calendar situation | POSE |
|---|---|
| Normal workday | standing, wearing a tiny blue necktie, holding a plastic cup of milk tea |
| Weekend / rest day | curled up asleep next to a steaming teacup |
| Cold | hunched, wrapped in a big red knitted scarf, paws tucked in |
| Hot / sunny | sitting, fanning itself with a folding paper fan, tongue slightly out |
| Rain | holding a large open indigo-blue paper umbrella, small raincoat |
| Typhoon signal | holding a torch in one paw and a cup of instant noodles in the other, sleepy look |
| Chinese New Year | red lucky-money packet in both paws, small red festive hat |
| Mid-Autumn | holding a round paper lantern, looking up |
| Christmas | red Santa hat, small wrapped present |
| 冬至 (Winter Solstice) | holding a bowl of tangyuan, steam rising |

Start with 4: workday, weekend, cold and rain.

## 5. After generating

1. Save the best images into the `assets` folder as `cat-wave.png`, `cat-rain.png`, and so on.
2. Tell me the file names. I'll strip the white background, trim the edges and put the cat into the calendar (`mascotImg` in `data.js`).
3. If the cat doesn't look like yours, re-upload your photos and say specifically what's wrong ("the nose should be pink", "the tail is shorter") instead of re-rolling the whole prompt.
