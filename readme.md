# BeeKai Labs website

The website for BeeKai Labs: web design, AI and automation, and consulting for small businesses, nonprofits and public organizations.

It is a static site built with [Astro](https://astro.build) and [Tailwind CSS](https://tailwindcss.com). All text, prices and projects live in content files, so most updates need no code changes.

## Run it locally

Requires Node.js 22 or newer.

```bash
npm install
npm run dev
```

The site opens at `http://localhost:4321`. If that port is taken by another project, Astro uses the next free one and prints the address in the terminal.

## Commands

| Command               | What it does                                      |
| :-------------------- | :------------------------------------------------ |
| `npm run dev`         | Start the local dev server                        |
| `npm run build`       | Build the production site into `dist/`            |
| `npm run preview`     | Build, then serve the production site locally     |
| `npm run astro-check` | Check types and content schemas                   |
| `npm run format`      | Format the files in `src/`                        |

Run `npm run astro-check` and `npm run build` before you deploy.

## Pages

| Page                         | Address                           |
| :--------------------------- | :-------------------------------- |
| Home                         | `/`                               |
| Services and service details | `/services/`, `/services/[slug]/` |
| Industries                   | `/industries/`, `/industries/[slug]/` |
| Portfolio and case studies   | `/portfolio/`, `/portfolio/[slug]/` |
| Blog and posts               | `/blog/`, `/blog/[slug]/`         |
| Pricing                      | `/pricing/`                       |
| About Us                     | `/about/`                         |
| Contact Us                   | `/contact/`                       |
| Privacy Policy and Terms     | `/privacy/`, `/terms/`            |
| RSS feed                     | `/rss.xml`                        |

## Where to edit content

### Site settings

| What                                                        | File                         |
| :---------------------------------------------------------- | :--------------------------- |
| Site name, tagline, domain, logo, SEO defaults              | `src/config/config.toml`     |
| Email, phone and service area                               | `src/config/config.toml` (`settings.contactInfo`) |
| Show or hide homepage stats and testimonials                | `src/config/config.toml` (`showStats`, `showTestimonials`) |
| Header menu, footer Company links, legal links              | `src/config/menu.en.json`    |
| Social links                                                | `src/config/social.json`     |
| Button labels and small interface text                      | `src/i18n/en.json`           |
| Fonts                                                       | `src/config/fonts.json`      |
| Colors                                                      | `src/styles/theme.css`       |

### Data files

Each file in `src/content/data/` is the single source for one kind of content. Add, remove or edit an entry and every page that uses it updates.

| What                                         | File                       |
| :------------------------------------------- | :------------------------- |
| Service groups (also the Services dropdown)  | `service-groups.yml`       |
| Services                                     | `services.yml`             |
| Industries                                   | `industries.yml`           |
| Portfolio categories (the filter tabs)       | `portfolio-categories.yml` |
| Pricing: packages, care plans, add-ons       | `pricing.yml`              |
| Process steps                                | `process.yml`              |
| "Why work with us" items                     | `why-us.yml`               |
| Tools shown on the homepage                  | `tools.yml`                |
| Homepage stats                               | `stats.yml`                |

A service with `status: coming-soon` shows a "Coming soon" badge and has no detail page.

### Portfolio projects

One Markdown file per project in `src/content/portfolio/english/`. The file name is the address of the case study.

- `categories` uses ids from `portfolio-categories.yml`. A project can be in more than one.
- `featured: true` shows the project on the homepage (up to three).
- `liveUrl` adds the "Visit website" link.
- `coverImage` and `mobileImage` are the desktop and mobile screenshots. Projects without a screenshot show the `icon` instead.

### Blog posts

One Markdown file per post in `src/content/blog/english/`. Posts with `draft: true` appear only in `npm run dev`; set it to `false` to publish.

### Page text

| What                                           | Where                               |
| :--------------------------------------------- | :---------------------------------- |
| Page titles, intros and search descriptions    | `src/content/pages/english/`        |
| Section headings, intros and buttons           | `src/content/sections/english/`     |
| Homepage search title and description          | `src/content/homepage/english/-index.md` |

### Images

Images go in `src/assets/images/` and are referenced from content as `/images/...`. Portfolio screenshots are in `src/assets/images/portfolio/`.

To change the favicon, replace `src/assets/images/favicon.png` and run `npm run generate-favicons`.

## Placeholders

Content that is not final yet is marked `[TODO: ...]`, either in the text itself or in a comment next to it. To list every placeholder:

```bash
grep -rn "TODO" src/content src/config
```

## Deploy

The site builds to static files, so any static host works.

- Build command: `npm run build`
- Output folder: `dist`
- Node.js version: 22 or newer

Set the real domain as `baseUrl` in `src/config/config.toml` before you deploy. It is used for the sitemap, canonical links and social previews.

## Code conventions

`AGENTS.md` describes how the code is organized and the rules to follow when changing components, schemas and styles.

## License

See [LICENSE.md](LICENSE.md). That file must stay in the repository.
