import { defineCollection } from "astro:content";
import config from ".astro/config.generated.json";
import { button, sectionsSchema } from "./sections.schema";
import { file, glob } from "astro/loaders";
import { z } from "astro/zod";

const portfolioFolder = config.settings.portfolioFolder || "portfolio";
const blogFolder = config.settings.blogFolder || "blog";

// Universal Page Schema
export const page = z.object({
  title: z.string(),
  author: z.string().optional(),
  categories: z.array(z.string()).default(["others"]).optional(),
  tags: z.array(z.string()).default(["others"]).optional(),
  date: z.date().optional(), // example date format 2022-01-01 or 2022-01-01T00:00:00+00:00 (Year-Month-Day Hour:Minute:Second+Timezone)
  description: z.string().optional(),
  image: z.string().optional(),
  draft: z.boolean().optional(),
  button: button.optional(),
  metaTitle: z.string().optional(),
  metaDescription: z.string().optional(),
  robots: z.string().optional(),
  excludeFromSitemap: z.boolean().optional(),
  excludeFromCollection: z.boolean().optional(),
  customSlug: z.string().optional(),
  canonical: z.string().optional(),
  keywords: z.array(z.string()).optional(),
  disableTagline: z.boolean().optional(),
  customPage: z.boolean().optional(), // true: the page has its own route file in src/pages
  ...sectionsSchema,
});

// Pages collection schema
const pagesCollection = defineCollection({
  loader: glob({ base: "./src/content/pages", pattern: "**/*.{md,mdx}" }),
  schema: page,
});

// Data file helper: one YAML file per data set in src/content/data
const dataFile = (name: string) => file(`./src/content/data/${name}.yml`);

// Service groups
const serviceGroupsCollection = defineCollection({
  loader: dataFile("service-groups"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
    fullTitle: z.string(),
    summary: z.string(),
    headline: z.string(),
    intro: z.string(),
    icon: z.string(),
    faq: z
      .array(z.object({ question: z.string(), answer: z.string() }))
      .default([]),
  }),
});

// Services
const servicesCollection = defineCollection({
  loader: dataFile("services"),
  schema: z.object({
    order: z.number(),
    group: z.string(), // id of a service group
    title: z.string(),
    summary: z.string(),
    includes: z.array(z.string()).default([]),
    status: z.enum(["available", "coming-soon"]),
    whoFor: z.string().optional(),
    priceNote: z.string().optional(),
  }),
});

// Industries
const industriesCollection = defineCollection({
  loader: dataFile("industries"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
    audience: z.string(),
    icon: z.string(),
    benefit: z.string(),
    problems: z.array(z.string()),
    solutions: z.array(z.string()),
  }),
});

// Portfolio categories
const portfolioCategoriesCollection = defineCollection({
  loader: dataFile("portfolio-categories"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
  }),
});

// Process steps
const processCollection = defineCollection({
  loader: dataFile("process"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
    description: z.string(),
  }),
});

// "Why work with us" items
const whyUsCollection = defineCollection({
  loader: dataFile("why-us"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
    description: z.string(),
    icon: z.string(),
  }),
});

// Pricing blocks
const pricingCollection = defineCollection({
  loader: dataFile("pricing"),
  schema: z.object({
    order: z.number(),
    title: z.string(),
    note: z.string().optional(),
    items: z.array(
      z.object({
        name: z.string(),
        price: z.string(),
        timeline: z.string().optional(),
        popular: z.boolean().optional(),
        includes: z.array(z.string()).optional(),
      }),
    ),
  }),
});

// Tools shown in the homepage trust strip
const toolsCollection = defineCollection({
  loader: dataFile("tools"),
  schema: z.object({
    order: z.number(),
    name: z.string(),
  }),
});

// Homepage stats (hidden by default)
const statsCollection = defineCollection({
  loader: dataFile("stats"),
  schema: z.object({
    order: z.number(),
    value: z.string(),
    label: z.string(),
  }),
});

// Portfolio Collection
const portfolioCollection = defineCollection({
  // Load Markdown and MDX files in the `src/content/portfolio/` directory.
  loader: glob({
    base: `./src/content/${portfolioFolder}`,
    pattern: "**/*.{md,mdx}",
  }),
  schema: page.extend({
    client: z.string(),
    location: z.string().optional(),
    weight: z.number().optional(), // Display order
    categories: z.array(z.string()).min(1), // ids from portfolio-categories.yml
    industry: z.string().optional(), // id from industries.yml
    services: z.array(z.string()).default([]), // ids from services.yml
    summary: z.string(),
    challenge: z.string(),
    solution: z.string(),
    results: z.string(),
    liveUrl: z.url().optional(),
    coverImage: z.string().optional(), // Desktop screenshot
    mobileImage: z.string().optional(), // Mobile screenshot
    icon: z.string().optional(), // Lucide icon shown when there is no screenshot
    gallery: z.array(z.string()).default([]),
    status: z.enum(["Live", "Concept", "In progress"]),
    featured: z.boolean().default(false),
  }),
});

// Blog Collection
const blogCollection = defineCollection({
  loader: glob({
    base: `./src/content/${blogFolder}`,
    pattern: "**/*.{md,mdx}",
  }),
  schema: page.extend({
    description: z.string(),
    date: z.date(),
    author: z.string(),
    tags: z.array(z.string()).default([]),
    coverImage: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

// Export collections
export const collections = {
  [portfolioFolder]: portfolioCollection,
  portfolio: portfolioCollection,
  [blogFolder]: blogCollection,
  blog: blogCollection,

  serviceGroups: serviceGroupsCollection,
  services: servicesCollection,
  industries: industriesCollection,
  portfolioCategories: portfolioCategoriesCollection,
  process: processCollection,
  whyUs: whyUsCollection,
  pricing: pricingCollection,
  tools: toolsCollection,
  stats: statsCollection,

  pages: pagesCollection,
  sections: defineCollection({
    loader: glob({ base: "./src/content/sections", pattern: "**/*.{md,mdx}" }),
  }),
  homepage: defineCollection({
    loader: glob({ base: "./src/content/homepage", pattern: "**/*.{md,mdx}" }),
  }),
};
