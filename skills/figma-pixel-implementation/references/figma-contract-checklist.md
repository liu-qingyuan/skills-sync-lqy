# Figma Contract Checklist

Use this as a compact ledger format during implementation.

## Ledger template

| Area | Figma fact | Implementation selector/file | Verified by |
| --- | --- | --- | --- |
| Root crop | `288×759` | screenshot clip | Playwright screenshot |
| Primary rail | `x=0`, `w=52`, bg `#F5F5F7` | `nav[aria-label=...]` | computed style + rect |
| Secondary rail | `x=52`, `w=236`, bg `#FAFAFA` | `.secondary-sidebar` | computed style + rect |
| Active row | `h=38.5`, bg `#EDE9FF` | `.item.is-active` | computed style + rect |
| Active text | `#6B4EFF`, 13px, 600 | `.item.is-active .label` | computed style |
| Inactive text | `#666`, 13px, 400 | `.item:not(.is-active)` | computed style |
| Icon slot | exact x/y/w/h per node | `.item-icon[data-section=...]` | rect |
| Active icon asset | active SVG or active fill/stroke only for selected item | `.item.is-active img` or SVG path | src/fill/stroke assertion |
| Inactive icon asset | neutral SVG or `#666` fill/stroke for unselected items | `.item:not(.is-active) img` or SVG path | src/fill/stroke assertion |
| State transition | previous item reverts to inactive icon after another item is selected | click sequence | Playwright interaction |
| Active dot | `5×5`, `#6B4EFF`, exact x/y | `.item-dot` | rect + style |
| Exception | e.g. storage footer retained | `.storage-footer` | visibility/text |

## Playwright helpers

```ts
async function expectRectNear(page, selector, expected, tolerance = 1.25) {
  const rect = await page.locator(selector).first().evaluate((node) => {
    const box = node.getBoundingClientRect();
    return { x: box.x, y: box.y, width: box.width, height: box.height };
  });
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (typeof expectedValue !== 'number') continue;
    expect(Math.abs(rect[key] - expectedValue), `${selector} ${key}`).toBeLessThanOrEqual(tolerance);
  }
}

async function expectStyle(page, selector, prop, expected) {
  const value = await page.locator(selector).first().evaluate(
    (node, property) => getComputedStyle(node).getPropertyValue(property),
    prop,
  );
  expect(value.trim(), `${selector} ${prop}`).toBe(expected);
}
```

## Selector guidance

- Prefer stable route hrefs, data attributes, roles, and component classes.
- Avoid translated `title` selectors for layout contracts unless locale is fixed.
- Add `data-section` or equivalent when it makes Figma node-to-DOM mapping unambiguous.

## Asset inspection

Before using an exported SVG:

```bash
head -20 asset.svg
grep -E '<svg|viewBox|width=|height=|fill=|stroke=' asset.svg | head -20
```

Reject or crop exports that include unrelated canvas, hidden active bars, extra whitespace, swapped node content, or an active-colored icon used as an inactive/default asset.

## State asset assertions

For any nav/list where Figma changes icon color on selection, assert both the initial state and a transition:

```ts
const activeIcon = await page.locator('.item-icon[data-section="cloud"] img').getAttribute('src');
expect(activeIcon).toContain('cloud-active');

await page.getByRole('button', { name: 'Local' }).click();
const previousIcon = await page.locator('.item-icon[data-section="cloud"] img').getAttribute('src');
expect(previousIcon).toContain('cloud-inactive');
const nextIcon = await page.locator('.item-icon[data-section="local"] img').getAttribute('src');
expect(nextIcon).toContain('local-active');
```

If assets are inline SVG instead of `img`, assert computed color or inspect `fill`/`stroke` on the rendered SVG paths.
