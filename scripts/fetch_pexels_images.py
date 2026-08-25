"""
Haalt een vaste set sfeerfoto's op via de Pexels API en verwerkt ze
tot geoptimaliseerde WebP/JPG-bestanden voor de site.

Vereist de omgevingsvariabele PEXELS_API_KEY (repo secret in GitHub Actions).
Wordt uitgevoerd door .github/workflows/fetch-pexels-images.yml.
"""
import io
import json
import os
import time

import requests
from PIL import Image, ImageEnhance

API_KEY = os.environ["PEXELS_API_KEY"]
OUT_DIR = "v2/images"

# Warme, gedempte kleurzweem die richting het merkpalet trekt
# (--bg: #F1EFE4, --koper: #A85A34) zodat foto's uit verschillende
# bronnen visueel bij elkaar horen.
GRADE_TINT = (222, 201, 173)
GRADE_TINT_ALPHA = 0.08
GRADE_SATURATION = 0.88
GRADE_CONTRAST = 1.04
GRADE_BRIGHTNESS = 1.01

# Elke entry komt overeen met een plek op de site (zie beeldplan).
# per_page > 1 zodat een niet-passend eerste resultaat (logo's, tekst,
# verkeerde doelgroep) overgeslagen kan worden via skip_first.
IMAGES = [
    {
        "filename": "hero-woonkamer",
        "query": "stack plain cardboard moving boxes cozy living room",
        "orientation": "portrait",
        "width": 1000,
        "height": 1250,
    },
    {
        "filename": "dienst-woningontruiming",
        "query": "movers carrying furniture out of house",
        "orientation": "landscape",
        "width": 1200,
        "height": 900,
    },
    {
        "filename": "dienst-sterfhuis",
        "query": "sorting old photographs hands memories box",
        "orientation": "portrait",
        "width": 1000,
        "height": 1250,
    },
    {
        "filename": "dienst-bezemschoon",
        "query": "empty clean apartment room bright hardwood floor",
        "orientation": "landscape",
        "width": 1200,
        "height": 675,
    },
    {
        "filename": "dienst-bedrijf",
        "query": "empty vacant office room no furniture windows",
        "orientation": "landscape",
        "width": 1200,
        "height": 675,
    },
    {
        "filename": "dienst-senioren",
        "query": "senior couple packing boxes moving house together",
        "orientation": "portrait",
        "width": 1000,
        "height": 1250,
    },
    {
        "filename": "dienst-spoed",
        "query": "movers loading furniture into van",
        "orientation": "landscape",
        "width": 1200,
        "height": 675,
    },
    {
        "filename": "contact-inventarisatie",
        "query": "writing notes laptop coffee home office",
        "orientation": "landscape",
        "width": 1000,
        "height": 750,
    },
]


def search_photo(query, orientation):
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": API_KEY},
        params={"query": query, "per_page": 5, "orientation": orientation},
        timeout=20,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"Geen Pexels-resultaten voor '{query}'")
    return photos[0]


def crop_to_ratio(img, target_w, target_h):
    src_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    return img.resize((target_w, target_h), Image.LANCZOS)


def apply_style(img):
    """Geeft elke foto, ongeacht bron of fotograaf, dezelfde uitstraling:
    licht gedempte kleuren, iets meer contrast en een warme zweem richting
    het merkpalet."""
    img = ImageEnhance.Color(img).enhance(GRADE_SATURATION)
    img = ImageEnhance.Contrast(img).enhance(GRADE_CONTRAST)
    img = ImageEnhance.Brightness(img).enhance(GRADE_BRIGHTNESS)
    tint_layer = Image.new("RGB", img.size, GRADE_TINT)
    return Image.blend(img, tint_layer, GRADE_TINT_ALPHA)


def download_and_process(photo, filename, target_w, target_h):
    img_resp = requests.get(photo["src"]["original"], timeout=30)
    img_resp.raise_for_status()
    img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
    img = crop_to_ratio(img, target_w, target_h)
    img = apply_style(img)

    os.makedirs(OUT_DIR, exist_ok=True)
    webp_path = os.path.join(OUT_DIR, f"{filename}.webp")
    jpg_path = os.path.join(OUT_DIR, f"{filename}.jpg")
    img.save(webp_path, "WEBP", quality=80)
    img.save(jpg_path, "JPEG", quality=82, optimize=True)
    print(f"{filename}: {os.path.getsize(webp_path) // 1024}KB webp, {os.path.getsize(jpg_path) // 1024}KB jpg")

    return {
        "filename": filename,
        "photographer": photo["photographer"],
        "photographer_url": photo["photographer_url"],
        "pexels_url": photo["url"],
    }


def main():
    credits = []
    for spec in IMAGES:
        print(f"Zoeken: {spec['query']}")
        photo = search_photo(spec["query"], spec["orientation"])
        credits.append(download_and_process(photo, spec["filename"], spec["width"], spec["height"]))
        time.sleep(1)

    with open(os.path.join(OUT_DIR, "credits.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, indent=2, ensure_ascii=False)
    print("Klaar. Credits weggeschreven naar v2/images/credits.json")


if __name__ == "__main__":
    main()
