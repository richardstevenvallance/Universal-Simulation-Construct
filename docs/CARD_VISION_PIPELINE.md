# Card Vision Pipeline

## Capture

- front and back photographs
- diffuse lighting
- neutral matte background
- fixed-distance guide
- optional Raspberry Pi camera stand for repeatability

## Detection

1. Detect the card quadrilateral.
2. Perspective-correct to a normalized rectangle.
3. Measure blur, glare and exposure quality.
4. OCR identifying text and collector number.
5. Match candidates against a card catalogue.

## Grading measurements

- Centering: compare border/frame geometry where the design supports it.
- Corners: whitening, rounding, bends and visible damage.
- Edges: chips, whitening and dents.
- Surface: scratches, print lines, stains, creases and indentations.

Full-art and borderless designs require design-specific templates; a generic border ratio must never be treated as authoritative.

## Output

- candidate identity + confidence
- measured defects + image coordinates
- provisional 1–10 estimate
- confidence
- reason list
- retained scan for manual review

The estimate must never be labelled as an official PSA, CGC or BGS grade.
