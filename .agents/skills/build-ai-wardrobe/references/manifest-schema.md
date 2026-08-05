# Wardrobe manifest schema

Use this JSON shape for the final `wardrobe.json`:

```json
{
  "version": 1,
  "title": "我的 AI 数字衣橱",
  "items": [
    {
      "id": "navy-knit-cardigan",
      "name": "藏蓝针织开衫",
      "category": "outerwear",
      "color": "#172033",
      "secondary_color": "#f2efe6",
      "tags": ["针织", "通勤", "开衫"],
      "image": "items/navy-knit-cardigan.png",
      "modeled_image": "modeled/navy-knit-cardigan.png",
      "source_refs": ["IMG_1284.jpg"],
      "status": "accepted",
      "notes": ""
    }
  ]
}
```

## Constraints

- Set `version` to `1`.
- Use a non-empty `title`.
- Use unique lowercase hyphenated `id` values.
- Use one of `tops`, `outerwear`, `bottoms`, `accessories`, or `shoes`.
- Use six-digit hexadecimal colors. Set `secondary_color` to `null` when absent.
- Keep at most 12 short tags.
- Store `image` and `modeled_image` as relative local paths below the manifest directory.
- Require `image` for accepted records. Allow an empty or omitted `modeled_image` when no identity reference was supplied.
- Use `accepted` only after visual QA. Use `hold` for unrecoverable or insufficiently evidenced garments.
- Keep `source_refs` as source basenames only; never place private absolute paths in a public case artifact.
