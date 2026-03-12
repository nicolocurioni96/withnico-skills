# Template Guide — Shotkit

## Choosing a Template

| Template | Best For | Vibe |
|----------|---------|------|
| `minimal` | Productivity, utilities, finance | Clean, trustworthy |
| `bold` | Games, lifestyle, fitness | Energetic, vibrant |
| `dark` | Pro tools, music, photography | Luxury, premium |
| `editorial` | Creative, travel, shopping | Magazine, editorial |
| `flat` | Photo/video, maps, AR | Immersive, UI-first |

## minimal
- Background: #F8F8F8
- UI: top 68% of canvas, rounded frame + shadow
- Text: below device, headline then subline

## bold
- Background: full-bleed gradient (deep blue → purple by default)
- Text: TOP of canvas
- UI: bottom 62%, rounded top corners
- Customize gradient in render_bold() in generate_screenshots.py

## dark
- Background: #0A0A0E near-black
- Colored glow halo behind device (default: blue)
- Text: below device

## editorial
- Background: #F5F2EE warm paper
- Left accent strip (default: red #FF5040)
- UI: right side, text: left side

## flat
- Full-bleed UI fills entire canvas
- Semi-transparent dark bar at bottom with text
- Best when your UI is visually stunning

## Custom Fonts
Add any .ttf to assets/fonts/ and update _get_font() in generate_screenshots.py.
Good free options: Inter, Space Grotesk, Sora, Outfit, Plus Jakarta Sans
