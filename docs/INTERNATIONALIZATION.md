# EVDB Internationalization Guide

## Overview

This guide explains how to implement multi-language support in EVDB using Hugo's built-in i18n capabilities.

## Hugo Configuration

### config.toml Updates

```toml
baseURL = 'https://evdb.gaiagreen.tech/'
defaultContentLanguage = 'en'
title = 'Public domain EV database'

# Enable multiple languages
[languages]
  [languages.en]
    languageName = "English"
    contentDir = "content/en"
    weight = 1
    [languages.en.params]
      description = "Open database of electric vehicles"
  
  [languages.de]
    languageName = "Deutsch"
    contentDir = "content/de"
    weight = 2
    title = "Öffentliche EV-Datenbank"
    [languages.de.params]
      description = "Offene Datenbank für Elektrofahrzeuge"
  
  [languages.pl]
    languageName = "Polski"
    contentDir = "content/pl"
    weight = 3
    title = "Publiczna baza danych pojazdów elektrycznych"
    [languages.pl.params]
      description = "Otwarta baza danych pojazdów elektrycznych"
  
  [languages.fr]
    languageName = "Français"
    contentDir = "content/fr"
    weight = 4
    title = "Base de données publique des véhicules électriques"
    [languages.fr.params]
      description = "Base de données ouverte des véhicules électriques"

[taxonomies]
manufacturer = "manufacturers"

[outputs]
page = ['html', 'json']
section = ['html', 'json']
home = ['html', 'json']
```

## Directory Structure

```
content/
  en/                          # English (default)
    vehicles/
      opel-mokka-e.md
    manufacturers/
      opel/
        _index.md
  de/                          # German
    vehicles/
      opel-mokka-e.md
    manufacturers/
      opel/
        _index.md
  pl/                          # Polish
    vehicles/
      opel-mokka-e.md
    manufacturers/
      opel/
        _index.md
  
i18n/                          # Translation strings
  en.toml
  de.toml
  pl.toml
  fr.toml
```

## Translation Files

### i18n/en.toml

```toml
[battery]
other = "Battery"

[battery_capacity]
other = "Capacity"

[battery_chemistry]
other = "Chemistry"

[range]
other = "Range"

[range_wltp]
other = "WLTP Range"

[range_real_world]
other = "Real-World Range"

[performance]
other = "Performance"

[power]
other = "Power"

[torque]
other = "Torque"

[acceleration]
other = "0-100 km/h"

[top_speed]
other = "Top Speed"

[charging]
other = "Charging"

[charging_ac]
other = "AC Charging"

[charging_dc]
other = "DC Fast Charging"

[dimensions]
other = "Dimensions"

[length]
other = "Length"

[width]
other = "Width"

[height]
other = "Height"

[weight]
other = "Weight"

[seating]
other = "Seating Capacity"

[cargo]
other = "Cargo Volume"

[pricing]
other = "Pricing"

[msrp]
other = "MSRP"

[incentives]
other = "Available Incentives"

[market_availability]
other = "Market Availability"

[available]
other = "Available"

[discontinued]
other = "Discontinued"

[announced]
other = "Announced"
```

### i18n/de.toml

```toml
[battery]
other = "Batterie"

[battery_capacity]
other = "Kapazität"

[battery_chemistry]
other = "Chemie"

[range]
other = "Reichweite"

[range_wltp]
other = "WLTP-Reichweite"

[range_real_world]
other = "Realistische Reichweite"

[performance]
other = "Leistung"

[power]
other = "Leistung"

[torque]
other = "Drehmoment"

[acceleration]
other = "0-100 km/h"

[top_speed]
other = "Höchstgeschwindigkeit"

[charging]
other = "Laden"

[charging_ac]
other = "AC-Laden"

[charging_dc]
other = "DC-Schnellladen"

[dimensions]
other = "Abmessungen"

[length]
other = "Länge"

[width]
other = "Breite"

[height]
other = "Höhe"

[weight]
other = "Gewicht"

[seating]
other = "Sitzplätze"

[cargo]
other = "Kofferraumvolumen"

[pricing]
other = "Preise"

[msrp]
other = "UVP"

[incentives]
other = "Fördermöglichkeiten"

[market_availability]
other = "Marktverfügbarkeit"

[available]
other = "Verfügbar"

[discontinued]
other = "Eingestellt"

[announced]
other = "Angekündigt"
```

### i18n/pl.toml

```toml
[battery]
other = "Bateria"

[battery_capacity]
other = "Pojemność"

[battery_chemistry]
other = "Chemia"

[range]
other = "Zasięg"

[range_wltp]
other = "Zasięg WLTP"

[range_real_world]
other = "Zasięg rzeczywisty"

[performance]
other = "Osiągi"

[power]
other = "Moc"

[torque]
other = "Moment obrotowy"

[acceleration]
other = "0-100 km/h"

[top_speed]
other = "Prędkość maksymalna"

[charging]
other = "Ładowanie"

[charging_ac]
other = "Ładowanie AC"

[charging_dc]
other = "Szybkie ładowanie DC"

[dimensions]
other = "Wymiary"

[length]
other = "Długość"

[width]
other = "Szerokość"

[height]
other = "Wysokość"

[weight]
other = "Masa"

[seating]
other = "Liczba miejsc"

[cargo]
other = "Pojemność bagażnika"

[pricing]
other = "Cennik"

[msrp]
other = "Cena katalogowa"

[incentives]
other = "Dostępne dopłaty"

[market_availability]
other = "Dostępność rynkowa"

[available]
other = "Dostępny"

[discontinued]
other = "Wycofany"

[announced]
other = "Zapowiedziany"
```

## Content Translation Example

### English: content/en/vehicles/opel-mokka-e.md

```yaml
---
title: Opel Mokka-e
manufacturer: ['Opel']
body: SUV
segment: JB
description: "Compact electric SUV with bold design and 330 km WLTP range"

battery:
  capacity_kwh: 50
  chemistry: "NMC"

# ... (technical specs remain the same)
---

## Overview

The Opel Mokka-e is a compact electric SUV that combines Opel's signature bold "Vizor" design with practical electric mobility.

## Design Philosophy

The Mokka-e showcases Opel's new design language...
```

### German: content/de/vehicles/opel-mokka-e.md

```yaml
---
title: Opel Mokka-e
manufacturer: ['Opel']
body: SUV
segment: JB
description: "Kompakter Elektro-SUV mit mutigem Design und 330 km WLTP-Reichweite"

battery:
  capacity_kwh: 50
  chemistry: "NMC"

# ... (technical specs remain the same - no translation needed)
---

## Übersicht

Der Opel Mokka-e ist ein kompakter Elektro-SUV, der Opels charakteristisches, mutiges "Vizor"-Design mit praktischer Elektromobilität verbindet.

## Design-Philosophie

Der Mokka-e präsentiert Opels neue Designsprache...
```

### Polish: content/pl/vehicles/opel-mokka-e.md

```yaml
---
title: Opel Mokka-e
manufacturer: ['Opel']
body: SUV
segment: JB
description: "Kompaktowy elektryczny SUV z odważnym designem i zasięgiem 330 km WLTP"

battery:
  capacity_kwh: 50
  chemistry: "NMC"

# ... (specyfikacje techniczne pozostają takie same)
---

## Opis

Opel Mokka-e to kompaktowy elektryczny SUV, który łączy charakterystyczny, odważny design „Vizor" marki Opel z praktyczną elektromobilnością.

## Filozofia designu

Mokka-e prezentuje nowy język projektowania Opla...
```

## Template Updates

### layouts/_default/single.html

```html
{{ define "main" }}
<article>
  <h1>{{ .Title }}</h1>
  
  <!-- Language switcher -->
  <nav class="language-switcher">
    {{ range .AllTranslations }}
      <a href="{{ .Permalink }}" {{ if eq .Lang $.Lang }}class="active"{{ end }}>
        {{ .Language.LanguageName }}
      </a>
    {{ end }}
  </nav>
  
  <!-- Battery Section -->
  <section class="battery">
    <h2>{{ i18n "battery" }}</h2>
    <dl>
      <dt>{{ i18n "battery_capacity" }}</dt>
      <dd>{{ .Params.battery.capacity_kwh }} kWh</dd>
      
      <dt>{{ i18n "battery_chemistry" }}</dt>
      <dd>{{ .Params.battery.chemistry }}</dd>
    </dl>
  </section>
  
  <!-- Range Section -->
  <section class="range">
    <h2>{{ i18n "range" }}</h2>
    <dl>
      <dt>{{ i18n "range_wltp" }}</dt>
      <dd>{{ .Params.range.wltp_km }} km</dd>
    </dl>
  </section>
  
  <!-- Content (translated) -->
  <div class="content">
    {{ .Content }}
  </div>
</article>
{{ end }}
```

## API Output

### JSON Output with Language

Update `layouts/vehicles/item.json`:

```json
{
  "name": "{{ .Title }}",
  "language": "{{ .Lang }}",
  "translations": [
    {{ range $index, $translation := .AllTranslations }}
    {{ if $index }},{{ end }}
    {
      "lang": "{{ $translation.Lang }}",
      "url": "{{ $translation.Permalink }}"
    }
    {{ end }}
  ],
  "body": "{{ .Params.body }}",
  "segment": "{{ .Params.segment }}",
  "description": "{{ .Params.description }}",
  "battery": {
    "capacity_kwh": {{ .Params.battery.capacity_kwh }},
    "chemistry": "{{ .Params.battery.chemistry }}"
  },
  "permalink": "{{ .Permalink }}"
}
```

## URL Structure

Hugo will generate URLs like:

```
/en/vehicles/opel-mokka-e/
/de/vehicles/opel-mokka-e/
/pl/vehicles/opel-mokka-e/
```

Or with subdomain approach:

```
en.evdb.gaiagreen.tech/vehicles/opel-mokka-e/
de.evdb.gaiagreen.tech/vehicles/opel-mokka-e/
pl.evdb.gaiagreen.tech/vehicles/opel-mokka-e/
```

## Translation Workflow

### 1. Create Base Content (English)

```bash
hugo new content/en/vehicles/new-vehicle.md
# Edit content, add technical specs, write description
```

### 2. Translate Key Fields

Create German version:

```bash
cp content/en/vehicles/new-vehicle.md content/de/vehicles/new-vehicle.md
# Translate: title, description, and content sections
# Keep technical specs identical (they're universal)
```

### 3. Quality Check

- Verify all translations exist for the same vehicle
- Check that technical specs are consistent across languages
- Ensure images are referenced correctly
- Test language switcher functionality

## Best Practices

### What to Translate

✅ **Translate:**
- Page titles
- Descriptions
- Content sections (overview, features, etc.)
- UI labels (via i18n files)

❌ **Don't Translate:**
- Technical specifications (numbers, measurements)
- Enum values (keep as English constants)
- Manufacturer names (unless there's an official localized name)
- URLs (keep in English for consistency)

### Handling Market-Specific Content

For content that differs by market (not just language):

```yaml
# content/de/vehicles/opel-mokka-e.md
market_specific:
  charging_infrastructure: "Mit über 50.000 Ladepunkten in Deutschland..."
  incentives_note: "Informationen zu aktuellen Förderungen finden Sie beim BAFA."

# content/pl/vehicles/opel-mokka-e.md
market_specific:
  charging_infrastructure: "Z ponad 2.000 punktami ładowania w Polsce..."
  incentives_note: "Aktualne informacje o dopłatach dostępne w NFOŚiGW."
```

## Maintenance

### Adding a New Language

1. Add language to `config.toml`
2. Create `i18n/[lang].toml` translation file
3. Create `content/[lang]/` directory structure
4. Start with top 50 most important vehicles
5. Gradually translate more content

### Keeping Translations in Sync

- Use version control to track when English content changes
- Implement a "needs translation" flag in front matter:
  ```yaml
  translation_status: "outdated"  # or "current"
  translation_last_sync: "2024-02-06"
  ```

### Automation Opportunities

- Use DeepL API for initial translation drafts
- Implement CI check for missing translations
- Create "translation coverage" report
- Track which vehicles are available in which languages
