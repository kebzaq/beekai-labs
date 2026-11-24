// Placeholder text such as "[TODO: client]" is fine while building the site,
// but must never reach visitors. These helpers keep it visible in `npm run dev`
// and drop it from production builds.

export const isTodo = (value?: string | null): boolean =>
  typeof value === "string" && value.includes("[TODO");

// The value, or undefined when it still holds a TODO placeholder in a production build
export const ready = <T extends string | null | undefined>(
  value: T,
): T | undefined => (isTodo(value) && !import.meta.env.DEV ? undefined : value);
