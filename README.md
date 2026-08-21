# Zorgzaam Ontruimd — website

Statische website voor Zorgzaam Ontruimd, huisontruiming en bezemschone oplevering.

## Structuur

```
/            → verwijst automatisch door naar /v2/ (huidige, actieve versie)
/v2/         → huidige website + landingspagina's (warm kalkwit/roestkoper design)
  index.html               → hoofdwebsite
  landing-google-ads.html  → landingspagina voor Google Ads campagnes
  landing-meta-ads.html    → landingspagina voor Meta (Facebook/Instagram) campagnes
/v1/         → vorige versie (zandsteen/mosgroen design), bewaard ter referentie
```

## Live zetten met GitHub Pages

1. Ga naar **Settings → Pages** in deze repository.
2. Kies bij **Source**: `Deploy from a branch`.
3. Kies branch `main` en map `/ (root)`.
4. Sla op. De site is na een paar minuten bereikbaar op `https://<gebruikersnaam>.github.io/<repository-naam>/`.

## Nog te doen voor livegang

- Telefoonnummer en e-mailadres invullen (nu `[telefoonnummer volgt]` / `[e-mailadres volgt]` op meerdere plekken in elk bestand).
- Contactformulieren koppelen aan een verzendservice (bijv. Formspree of Web3Forms) — nu versturen ze nog nergens naartoe.
- Eigen domein koppelen via **Settings → Pages → Custom domain** zodra bekend.
- Canonical-URL's in de `<head>` van elk bestand aanpassen naar het echte domein.
