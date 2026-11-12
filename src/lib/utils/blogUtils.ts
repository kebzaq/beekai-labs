import slugify from "slugify";

// URL-safe id of a tag, used by the tag filter
export const tagId = (tag: string) =>
  slugify(tag, { lower: true, strict: true });

// Estimated reading time in minutes (about 200 words per minute)
export const readingTime = (text = "") =>
  Math.max(1, Math.ceil(text.trim().split(/\s+/).filter(Boolean).length / 200));

// Post date such as "12 Nov 2026". Dates in frontmatter are UTC, so they are formatted in UTC.
export const formatPostDate = (date: Date) =>
  date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
