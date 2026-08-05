#!/usr/bin/env python3
"""Validate a local wardrobe manifest and build a self-contained HTML gallery."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path, PurePosixPath
import re
import sys


CATEGORIES = {
    "tops": "上装",
    "outerwear": "外套",
    "bottoms": "下装",
    "accessories": "配饰",
    "shoes": "鞋履",
}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"manifest not found: {path}")
    except json.JSONDecodeError as error:
        fail(f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}")
    if not isinstance(data, dict):
        fail("manifest root must be an object")
    return data


def safe_relative(raw: object, field: str, required: bool) -> str:
    if raw in (None, "") and not required:
        return ""
    if not isinstance(raw, str) or not raw.strip():
        fail(f"{field} must be a non-empty relative image path")
    value = raw.strip().replace("\\", "/")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ":" in value or value.startswith("//"):
        fail(f"{field} must stay below the manifest directory: {raw}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        fail(f"{field} must point to a supported image: {raw}")
    return path.as_posix()


def validate(data: dict, manifest_path: Path, output_path: Path) -> dict:
    if data.get("version") != 1:
        fail("version must be 1")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        fail("title must be a non-empty string")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("items must be a non-empty array")

    normalized = []
    seen_ids = set()
    root = manifest_path.parent.resolve()
    output_dir = output_path.parent.resolve()
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            fail(f"items[{index}] must be an object")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
            fail(f"items[{index}].id must be lowercase hyphenated text")
        if item_id in seen_ids:
            fail(f"duplicate item id: {item_id}")
        seen_ids.add(item_id)

        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            fail(f"items[{index}].name must be non-empty")
        category = item.get("category")
        if category not in CATEGORIES:
            fail(f"items[{index}].category must be one of: {', '.join(CATEGORIES)}")
        color = item.get("color")
        if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
            fail(f"items[{index}].color must be a six-digit hex value")
        secondary = item.get("secondary_color")
        if secondary is not None and (not isinstance(secondary, str) or not COLOR_PATTERN.fullmatch(secondary)):
            fail(f"items[{index}].secondary_color must be null or a six-digit hex value")
        tags = item.get("tags", [])
        if not isinstance(tags, list) or len(tags) > 12 or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            fail(f"items[{index}].tags must contain at most 12 non-empty strings")
        status = item.get("status", "accepted")
        if status not in {"accepted", "hold"}:
            fail(f"items[{index}].status must be accepted or hold")

        image_path = safe_relative(item.get("image"), f"items[{index}].image", status == "accepted")
        modeled_path = safe_relative(item.get("modeled_image"), f"items[{index}].modeled_image", False)
        if status == "accepted":
            source_image = (root / image_path).resolve()
            if root not in source_image.parents or not source_image.is_file():
                fail(f"missing image for {item_id}: {source_image}")
            render_image = Path(source_image).relative_to(output_dir).as_posix() if output_dir in source_image.parents else Path(__import__('os').path.relpath(source_image, output_dir)).as_posix()
        else:
            render_image = ""

        render_modeled = ""
        if modeled_path:
            source_modeled = (root / modeled_path).resolve()
            if root not in source_modeled.parents or not source_modeled.is_file():
                fail(f"missing modeled image for {item_id}: {source_modeled}")
            render_modeled = Path(source_modeled).relative_to(output_dir).as_posix() if output_dir in source_modeled.parents else Path(__import__('os').path.relpath(source_modeled, output_dir)).as_posix()

        normalized.append({
            "id": item_id,
            "name": name.strip(),
            "category": category,
            "category_label": CATEGORIES[category],
            "color": color.lower(),
            "secondary_color": secondary.lower() if secondary else None,
            "tags": [tag.strip() for tag in tags],
            "image": render_image,
            "modeled_image": render_modeled,
            "status": status,
            "notes": str(item.get("notes", "")).strip(),
        })

    return {
        "version": 1,
        "title": title.strip(),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "items": normalized,
    }


def build_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<", "\\u003c")
    title = html.escape(data["title"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--paper:#f2efe7;--ink:#262b24;--muted:#77786f;--line:#d8d3c7;--sage:#5f6f52;--terracotta:#c86f4a;--card:#faf8f2}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
.shell{{max-width:1420px;margin:auto;padding:34px}} header{{display:grid;grid-template-columns:1fr auto;gap:28px;align-items:end;border-bottom:1px solid var(--line);padding-bottom:28px}}
.eyebrow{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--terracotta);font-weight:700}} h1{{font:clamp(44px,8vw,104px)/.92 Georgia,serif;letter-spacing:-.055em;margin:8px 0 0;max-width:900px}}
.count{{font:64px/1 Georgia,serif;color:var(--sage);text-align:right}} .count span{{display:block;font:12px/1.3 system-ui;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:6px}}
.toolbar{{display:flex;gap:12px;align-items:center;justify-content:space-between;margin:24px 0;flex-wrap:wrap}} .filters{{display:flex;gap:7px;flex-wrap:wrap}}
button,input{{font:inherit}} button{{border:1px solid var(--line);background:transparent;border-radius:999px;padding:8px 14px;color:var(--ink);cursor:pointer}} button.active{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}
input{{min-width:260px;border:0;border-bottom:1px solid var(--ink);background:transparent;padding:9px 2px;outline:none}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}} .card{{background:var(--card);border:1px solid var(--line);min-width:0}}
.visual{{aspect-ratio:4/5;display:grid;place-items:center;overflow:hidden;background:linear-gradient(145deg,#f8f5ed,#e8e2d5)}} .visual img{{width:100%;height:100%;object-fit:contain;padding:8%;transition:transform .35s ease}} .card:hover .visual img{{transform:scale(1.025)}}
.meta{{display:grid;grid-template-columns:1fr auto;gap:8px;padding:14px 15px 16px;border-top:1px solid var(--line)}} .meta h2{{font:20px/1.2 Georgia,serif;margin:0}} .category{{color:var(--muted);font-size:12px;margin-top:5px}} .swatches{{display:flex;gap:5px}} .swatch{{width:16px;height:16px;border-radius:50%;border:1px solid #0002}}
.tags{{grid-column:1/-1;display:flex;gap:5px;flex-wrap:wrap;margin-top:3px}} .tag{{font-size:11px;color:var(--muted);border:1px solid var(--line);padding:2px 7px;border-radius:999px}}
.empty{{grid-column:1/-1;padding:80px 20px;text-align:center;color:var(--muted);border:1px dashed var(--line)}}
dialog{{border:0;padding:0;background:var(--card);box-shadow:0 30px 80px #0005;max-width:min(900px,92vw)}} dialog::backdrop{{background:#171914cc}} dialog img{{display:block;max-width:100%;max-height:82vh;object-fit:contain}} .close{{position:absolute;right:12px;top:12px;background:var(--paper)}}
footer{{display:flex;justify-content:space-between;color:var(--muted);border-top:1px solid var(--line);margin-top:38px;padding:18px 0;font-size:12px}}
@media(max-width:1000px){{.grid{{grid-template-columns:repeat(3,1fr)}}}} @media(max-width:720px){{.shell{{padding:22px 16px}}header{{grid-template-columns:1fr}}.count{{text-align:left}}.grid{{grid-template-columns:repeat(2,1fr)}}input{{width:100%}}}} @media(max-width:430px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body><main class="shell"><header><div><div class="eyebrow">Marvis · Local AI Wardrobe</div><h1>{title}</h1></div><div class="count" id="count">0<span>pieces collected</span></div></header>
<section class="toolbar"><div class="filters" id="filters"></div><label><span class="eyebrow">搜索</span><br><input id="search" type="search" placeholder="名称、颜色或标签"></label></section>
<section class="grid" id="grid"></section><footer><span>本地生成 · 无需 API Key</span><span>源照片不会写入此页面</span></footer></main>
<dialog id="viewer"><button class="close" type="button">关闭</button><img alt=""></dialog>
<script id="wardrobe-data" type="application/json">{payload}</script>
<script>
const data=JSON.parse(document.getElementById('wardrobe-data').textContent);const grid=document.getElementById('grid');const filters=document.getElementById('filters');const search=document.getElementById('search');const count=document.getElementById('count');let active='all';
const accepted=data.items.filter(x=>x.status==='accepted');const cats=[['all','全部'],...Object.entries(Object.fromEntries(accepted.map(x=>[x.category,x.category_label])))];
for(const [key,label] of cats){{const b=document.createElement('button');b.textContent=label;b.dataset.key=key;b.onclick=()=>{{active=key;document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('active',x.dataset.key===key));render()}};if(key==='all')b.className='active';filters.appendChild(b)}}
function render(){{const q=search.value.trim().toLowerCase();const items=accepted.filter(x=>(active==='all'||x.category===active)&&(!q||[x.name,x.category_label,...x.tags].join(' ').toLowerCase().includes(q)));grid.replaceChildren();count.firstChild.nodeValue=String(items.length);if(!items.length){{const e=document.createElement('div');e.className='empty';e.textContent='没有符合条件的衣物';grid.appendChild(e);return}}for(const x of items){{const card=document.createElement('article');card.className='card';const visual=document.createElement('button');visual.className='visual';visual.style.border='0';visual.style.padding='0';visual.style.borderRadius='0';const img=document.createElement('img');img.src=x.image;img.alt=x.name;visual.appendChild(img);visual.onclick=()=>openViewer(x.modeled_image||x.image,x.name);const meta=document.createElement('div');meta.className='meta';const text=document.createElement('div');const h=document.createElement('h2');h.textContent=x.name;const c=document.createElement('div');c.className='category';c.textContent=x.category_label;text.append(h,c);const swatches=document.createElement('div');swatches.className='swatches';for(const color of [x.color,x.secondary_color].filter(Boolean)){{const s=document.createElement('span');s.className='swatch';s.style.background=color;s.title=color;swatches.appendChild(s)}}const tags=document.createElement('div');tags.className='tags';for(const tag of x.tags){{const t=document.createElement('span');t.className='tag';t.textContent=tag;tags.appendChild(t)}}meta.append(text,swatches,tags);card.append(visual,meta);grid.appendChild(card)}}}}
const viewer=document.getElementById('viewer');function openViewer(src,name){{viewer.querySelector('img').src=src;viewer.querySelector('img').alt=name;viewer.showModal()}}viewer.querySelector('.close').onclick=()=>viewer.close();viewer.onclick=e=>{{if(e.target===viewer)viewer.close()}};search.addEventListener('input',render);render();
</script></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Path to wardrobe.json")
    parser.add_argument("--output", required=True, help="Output wardrobe.html path")
    parser.add_argument("--check-only", action="store_true", help="Validate without writing HTML")
    args = parser.parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    data = validate(read_manifest(manifest_path), manifest_path, output_path)
    if args.check_only:
        print(f"Validated {len(data['items'])} wardrobe items")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(data), encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Items: {sum(item['status'] == 'accepted' for item in data['items'])} accepted, {sum(item['status'] == 'hold' for item in data['items'])} held")


if __name__ == "__main__":
    main()
