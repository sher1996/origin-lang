# Export Diagram as PNG

The Visual Editor now supports exporting your block diagram as a PNG image.

## How to Use

- Click the **Export → PNG** button in the top-right toolbar (Image icon).
- The PNG will be downloaded automatically, named `diagram-YYYYMMDD_HHmm.png`.
- If your browser supports it, the PNG is also copied to your clipboard (see toast message).

## Theme Fidelity

- The exported PNG matches your current light/dark theme.
- Transparent backgrounds are preserved for best results.

## Edge Cases

- **Large diagrams** (>8k × 8k px): a warning is shown and export is blocked.
- **Mobile Safari**: only download is supported (no clipboard copy).

## Screenshot

![Export PNG button screenshot](./export-png-screenshot.png)

## Browser Support

- Clipboard copy requires `navigator.clipboard.write` and `ClipboardItem` (most modern browsers).
- If not available, only download is performed.

---

For more, see the [Visual Editor guide](./getting-started.md). 