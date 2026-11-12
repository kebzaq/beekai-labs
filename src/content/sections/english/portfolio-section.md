---
# Portfolio grid. Projects come from src/content/portfolio and tabs from src/content/data/portfolio-categories.yml
enable: true
title: "Our Work"
description: "A look at what we are building for local businesses and organizations."
allLabel: "All" # Label of the first tab

options:
  featuredOnly: true # true: only projects with `featured: true`
  limit: 3 # Maximum number of projects, or false for no limit
  grouped: false # true: under "All", show projects under a heading per category

button:
  # Refer to sharedButton in src/sections.schema.ts for all options.
  enable: true
  label: "See all projects"
  url: "/portfolio/"
  variant: "outline"
---
