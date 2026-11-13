import { z } from "astro/zod";

export const sharedButton = z
  .object({
    enable: z.boolean().optional(),
    tag: z.enum(["a", "button"]).optional(),
    url: z.string().optional(),
    label: z.string(),
    class: z.string().optional(),
    rel: z.string().optional(),
    icon: z.string().optional(),
    target: z.string().optional(),
    hoverEffect: z
      .enum(["text-flip", "creative-fill", "magnetic", "magnetic-text-flip"])
      .optional(),
    variant: z.enum(["fill", "outline", "text", "circle"]).optional(),
  })
  .loose();

export const sharedButtonTag = sharedButton.refine(
  (data) => data.tag !== "a" || !!data.url,
  {
    message: "`url` is required when `tag` is 'a'",
    path: ["url"],
  },
);

export const AppearanceEnum = z.enum(["dark", "light"]);
export const button = sharedButtonTag;

export const videoConfigSchema = z.object({
  src: z.string(),
  type: z.string().optional(),
  provider: z.enum(["youtube", "vimeo", "html5"]).optional(),
  poster: z.string().optional(),
  autoplay: z.boolean().optional(),
  id: z.string().optional(),
});

export const inputFieldSchema = z.object({
  label: z.string().optional(),
  placeholder: z.string().optional(),
  required: z.boolean().optional(),
  halfWidth: z.boolean().optional(),
  defaultValue: z.string().optional(),
  name: z.string().optional(),
  selected: z.boolean().optional(),
  value: z.boolean().optional(),
  checked: z.boolean().optional(),
  type: z.enum(["text", "email", "radio", "checkbox"]).optional(),
  id: z.string().optional(),
  tag: z.literal("textarea").optional(),
  rows: z.string().optional(),
  group: z.string().optional(),
  groupLabel: z.string().optional(),
  items: z
    .array(
      z.object({
        label: z.string(),
        name: z.string().optional(),
        id: z.string().optional(),
        value: z.string().optional(),
        required: z.boolean().optional(),
        groupLabel: z.string().optional(),
        group: z.string().optional(),
        type: z.enum(["radio", "checkbox"]).optional(),
        halfWidth: z.boolean().optional(),
        defaultValue: z.string().optional(),
        checked: z.boolean().optional(),
      }),
    )
    .optional(),
  dropdown: z
    .object({
      type: z.enum(["select", "search"]).optional(),
      search: z
        .object({
          placeholder: z.string().optional(),
        })
        .optional(),
      items: z.array(
        z.object({
          label: z.string(),
          selected: z.literal(true),
          value: z.string(),
        }),
      ),
    })
    .optional(),
  content: z.string().optional(),
  note: z.enum(["info", "warning", "success", "deprecated", "hint"]).optional(),
  parentClass: z.string().optional(),
});

// ================================================================================
// SECTIONS SCHEMA
// ================================================================================

export const contactFormSchema = z.object({
  action: z.string().optional(),
  emailSubject: z.string().optional(),
  note: z.string().optional(),
  submitButton: z.object({
    label: z.string(),
  }),
  inputs: z.array(inputFieldSchema),
});

// Fields shared by most sections
export const baseSectionSchema = z
  .object({
    enable: z.boolean(),
    title: z.string(),
    description: z.string(),
    button: sharedButton,
  })
  .partial();

export const bannerAgencySectionSchema = baseSectionSchema
  .extend({
    titleSize: z.enum(["display-1", "display-2", "display-3"]).optional(),
    image: z.string().optional(),
    secondaryButton: sharedButton.optional(),
    note: z.string().optional(),
  })
  .optional();

export const industriesSectionSchema = baseSectionSchema
  .extend({ cardLinkLabel: z.string().optional() })
  .optional();

export const toolsSectionSchema = baseSectionSchema.optional();

export const whyUsSectionSchema = baseSectionSchema.optional();

export const industryDetailsSectionSchema = baseSectionSchema
  .extend({ blockLinkLabel: z.string().optional() })
  .optional();

export const servicesSectionSchema = baseSectionSchema
  .extend({ cardLinkLabel: z.string().optional() })
  .optional();

export const statsSectionSchema = baseSectionSchema.optional();

export const portfolioSectionSchema = baseSectionSchema
  .extend({
    allLabel: z.string().optional(),
    options: z
      .object({
        featuredOnly: z.boolean(),
        limit: z.union([z.number().int(), z.literal(false)]),
        grouped: z.boolean(),
      })
      .partial()
      .optional(),
  })
  .optional();

export const testimonialsSectionSchema = baseSectionSchema
  .extend({
    list: z
      .array(
        z.object({
          quote: z.string(),
          name: z.string(),
          role: z.string().optional(),
        }),
      )
      .optional(),
  })
  .optional();

export const processSectionSchema = baseSectionSchema.optional();

export const contactSectionSchema = baseSectionSchema
  .extend({
    note: z.string().optional(),
    form: contactFormSchema.optional(),
  })
  .optional();

export const ctaSectionSchema = baseSectionSchema.optional();

export const pricingSectionSchema = baseSectionSchema
  .extend({ popularLabel: z.string().optional() })
  .optional();

export const serviceGroupsSectionSchema = baseSectionSchema
  .extend({
    jumpMenuLabel: z.string().optional(),
    learnMoreLabel: z.string().optional(),
    comingSoonLabel: z.string().optional(),
  })
  .optional();

export const aboutSectionSchema = baseSectionSchema
  .extend({
    mission: z
      .object({
        title: z.string(),
        description: z.string(),
        tagline: z.string(),
      })
      .partial()
      .optional(),
  })
  .optional();

export const storySectionSchema = baseSectionSchema
  .extend({
    // Honeycomb visual: the name parts and the name they combine into
    nameParts: z
      .array(z.object({ label: z.string(), note: z.string().optional() }))
      .optional(),
    nameResult: z.string().optional(),
  })
  .optional();

export const valuesSectionSchema = baseSectionSchema
  .extend({
    list: z
      .array(
        z.object({
          icon: z.string().optional(),
          title: z.string(),
          description: z.string().optional(),
        }),
      )
      .optional(),
  })
  .optional();

export const teamSectionSchema = baseSectionSchema
  .extend({
    focusLabel: z.string().optional(),
    list: z
      .array(
        z.object({
          name: z.string(),
          role: z.string().optional(),
          bio: z.string().optional(),
          focus: z.string().optional(),
          image: z.string().optional(),
        }),
      )
      .optional(),
  })
  .optional();

export const faqSectionSchema = baseSectionSchema.optional();

export const sectionsSchema = {
  bannerAgencySection: bannerAgencySectionSchema,
  industriesSection: industriesSectionSchema,
  toolsSection: toolsSectionSchema,
  whyUsSection: whyUsSectionSchema,
  industryDetailsSection: industryDetailsSectionSchema,
  servicesSection: servicesSectionSchema,
  statsSection: statsSectionSchema,
  portfolioSection: portfolioSectionSchema,
  testimonialsSection: testimonialsSectionSchema,
  processSection: processSectionSchema,
  contactSection: contactSectionSchema,
  ctaSection: ctaSectionSchema,
  pricingSection: pricingSectionSchema,
  serviceGroupsSection: serviceGroupsSectionSchema,
  aboutSection: aboutSectionSchema,
  storySection: storySectionSchema,
  valuesSection: valuesSectionSchema,
  teamSection: teamSectionSchema,
  faqSection: faqSectionSchema,
};
