# EVDB Enhancement Plan

## Overview
This document outlines planned improvements to the EVDB schema and structure based on feedback.

## 1. Country-Level Market Availability

### Current State
- No market availability tracking

### Proposed Changes
- Add `market_availability` field with array of country codes (ISO 3166-1 alpha-2)
- Support both current and discontinued markets with date ranges

### Example
```yaml
market_availability:
  - country: "DE"
    status: "available"
    available_since: "2021-01"
  - country: "PL"
    status: "available"
    available_since: "2021-06"
  - country: "GB"
    status: "discontinued"
    available_since: "2020-11"
    discontinued_on: "2024-12"
```

## 2. Standardized Enums for Common Fields

### Proposed Enums

#### Battery Chemistry
- `LFP` - Lithium Iron Phosphate
- `NMC` - Nickel Manganese Cobalt
- `NCA` - Nickel Cobalt Aluminum
- `LTO` - Lithium Titanate Oxide
- `SODIUM_ION` - Sodium-ion
- `SOLID_STATE` - Solid-state (future)
- `OTHER` - Other/Unknown (catch-all for new chemistries)

#### Drivetrain
- `FWD` - Front-wheel drive
- `RWD` - Rear-wheel drive
- `AWD` - All-wheel drive
- `4WD` - Four-wheel drive

#### Body Types
- `SEDAN` - Sedan/Saloon
- `HATCHBACK` - Hatchback
- `SUV` - Sport Utility Vehicle
- `CROSSOVER` - Crossover
- `COUPE` - Coupe
- `CONVERTIBLE` - Convertible
- `WAGON` - Station Wagon/Estate
- `VAN` - Van
- `PICKUP` - Pickup Truck
- `MINIBUS` - Minibus
- `BUS` - Bus
- `TRUCK` - Truck
- `OTHER` - Other

#### Charging Standards
- `CCS1` - Combined Charging System Type 1
- `CCS2` - Combined Charging System Type 2
- `CHADEMO` - CHAdeMO
- `TESLA_NACS` - Tesla NACS (North American Charging Standard)
- `TESLA_SCC` - Tesla Supercharger (proprietary)
- `GB_T` - GB/T (China)
- `TYPE1` - Type 1 (J1772)
- `TYPE2` - Type 2 (Mennekes)
- `OTHER` - Other

#### Fast Charging Speed Classes
- `NONE` - No DC fast charging
- `SLOW` - < 50 kW
- `MEDIUM` - 50-99 kW
- `FAST` - 100-149 kW
- `ULTRA_FAST` - 150-249 kW
- `HYPER_FAST` - 250+ kW

### Implementation Strategy
- Create `enums.json` in `api/v1/schema/`
- Use enum values in vehicle content, but validate against list
- Allow `OTHER` + custom string for future-proofing
- Regular reviews to add new enum values as technology evolves

## 3. Multiple Photos and Illustrations

### Current State
- Single image per vehicle (implied)

### Proposed Changes
- Add `images` array field with structured metadata
- Support multiple image types (exterior, interior, technical, press, user-submitted)
- Include image metadata (photographer, license, source URL)

### Example
```yaml
images:
  - type: "exterior"
    subtype: "front"
    url: "/images/opel-mokka-e-front.jpg"
    alt: "Opel Mokka-e front view"
    credit: "Opel Media"
    license: "CC BY-SA 4.0"
    source_url: "https://media.opel.com/..."
  - type: "exterior"
    subtype: "side"
    url: "/images/opel-mokka-e-side.jpg"
    alt: "Opel Mokka-e side profile"
  - type: "interior"
    subtype: "dashboard"
    url: "/images/opel-mokka-e-dashboard.jpg"
    alt: "Opel Mokka-e dashboard and infotainment"
  - type: "technical"
    subtype: "battery"
    url: "/images/opel-mokka-e-battery-diagram.svg"
    alt: "Battery pack diagram"
```

### Image Types
- `exterior` - Outside views (front, rear, side, three-quarter)
- `interior` - Inside views (dashboard, seats, cargo, details)
- `technical` - Diagrams, cutaways, technical illustrations
- `press` - Official press photos
- `render` - 3D renders or illustrations
- `user` - Community-submitted photos

## 4. Multi-Language Support

### Current State
- English only

### Proposed Strategy

#### Hugo i18n Support
- Use Hugo's built-in internationalization
- Create language-specific content directories
- Share technical data, translate descriptions

#### Directory Structure
```
content/
  en/
    vehicles/
      opel-mokka-e.md
    manufacturers/
      opel/
  de/
    vehicles/
      opel-mokka-e.md
    manufacturers/
      opel/
  pl/
    vehicles/
      opel-mokka-e.md
```

#### Shared Data Model
- Technical specs remain in one place (no translation needed)
- Translate: vehicle descriptions, feature names, marketing text
- Keep measurements in both metric and imperial

#### Supported Languages (Phase 1)
- English (en) - Base language
- German (de) - Major EV market
- Polish (pl) - Your home market
- French (fr) - EU major market
- Spanish (es) - EU major market

#### Supported Languages (Phase 2)
- Dutch (nl)
- Italian (it)
- Norwegian (no)
- Swedish (sv)
- Chinese (zh)

### Implementation
```yaml
# en/vehicles/opel-mokka-e.md
---
title: Opel Mokka-e
description: "Compact electric SUV with bold design and 330 km range"
manufacturer: ['Opel']
# ... technical specs (shared)
---

# de/vehicles/opel-mokka-e.md
---
title: Opel Mokka-e
description: "Kompakter Elektro-SUV mit mutigem Design und 330 km Reichweite"
manufacturer: ['Opel']
# ... same technical specs
---
```

## Implementation Phases

### Phase 1: Core Data Model Enhancement
- [ ] Create comprehensive vehicle schema with all proposed fields
- [ ] Define enum values in `enums.json`
- [ ] Update Hugo templates to use new fields
- [ ] Add validation scripts

### Phase 2: Multi-Media Support
- [ ] Implement image array structure
- [ ] Create image upload/management guidelines
- [ ] Set up image optimization pipeline
- [ ] Add gallery layouts

### Phase 3: Market Data
- [ ] Add country-level availability tracking
- [ ] Import historical market data where available
- [ ] Create market availability API endpoints

### Phase 4: Internationalization
- [ ] Set up Hugo i18n configuration
- [ ] Create translation workflow
- [ ] Translate core UI elements
- [ ] Add language switcher
- [ ] Start translating top 50 vehicles to German/Polish

### Phase 5: API Enhancement
- [ ] Update JSON API to include all new fields
- [ ] Add filtering by market, battery chemistry, etc.
- [ ] Create OpenAPI/Swagger documentation
- [ ] Version API (move to v2 if breaking changes needed)

## Backward Compatibility

- Keep existing simple fields for basic data entry
- Make new fields optional
- Provide migration scripts for existing content
- Support both old and new formats during transition

## Data Quality

- Create validation scripts for enum values
- Set up CI checks for data consistency
- Provide clear contribution guidelines
- Use GitHub Actions to validate PRs

## Future Considerations

- User-generated content (reviews, real-world range)
- Integration with charging network databases
- Mobile app support
- GraphQL API option
- Community translation platform integration
