# Image prompts

## Garment cutout

```text
Use case: background-extraction
Primary request: Reconstruct the exact target garment from the reference image as one complete empty clothing item.
Scene/backdrop: A perfectly flat solid KEY_COLOR chroma-key background.
Composition: Center the complete garment with generous padding; show the full silhouette and every visible extremity.
Fidelity: Preserve only source-supported color, material, proportions, construction, pattern, graphics, text, seams, closures and trim. Omit uncertain details instead of inventing them.
Remove: Person, skin, hair, mannequin, hanger, underlayers, adjacent garments, props, floor and scene.
Constraints: Uniform background with no gradient, texture, reflection, floor plane, cast shadow or contact shadow. Do not use KEY_COLOR anywhere in the garment. No watermark or added text.
```
Use a second reference only when it reveals construction that is missing from the primary view.

## Identity-preserving modeled image

```text
Use case: identity-preserve
Input images: Image 1 is the identity reference; Image 2 is the exact garment reference.
Primary request: Create a professional horizontal 3:2 editorial fashion photograph of the person in Image 1 wearing the exact garment from Image 2.
Identity: Preserve the recognizable face, hair, age, build, skin texture and body proportions.
Garment fidelity: Preserve color, material, fit, construction, pattern, graphics, logos, text, proportions, closure and distinctive details. Do not redesign or simplify it.
Styling: Use understated neutral supporting clothes that do not cover or compete with the featured item. Keep the complete featured item visible.
Scene: Tasteful real-world setting, warm natural light, realistic shadows and restrained editorial color grading.
Avoid: Crossed arms, bags or scarves covering the item, invented closures, fake text, cropped item extremities, extra people, watermark, text overlay or synthetic AI polish.
```
