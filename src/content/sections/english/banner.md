---
enable: true # Control the visibility of this section across all pages where it is used
titleSize: "display-3" # Options: "display-1" | "display-2" | "display-3" (use a smaller size for a longer title)
# Two lines, each a "block" span. The second line has the thin brand-orange outline (text-outline-accent).
# Each line is made of two phrases that don't break inside (whitespace-nowrap from md), so a line that
# doesn't fit breaks only between its phrases: "Websites," / "AI & Automation" and "Built for" / "Your Business.".
# Exception: on lg (1024-1279px) the text column is narrower than "AI & Automation", so it may break after "AI &".
# On phones the words wrap naturally.
title: '<span class="block"><span class="md:whitespace-nowrap">Websites,</span> <span class="md:whitespace-nowrap lg:whitespace-normal xl:whitespace-nowrap">AI&nbsp;& Automation</span></span><span class="text-outline-accent block"><span class="md:whitespace-nowrap">Built for</span> <span class="md:whitespace-nowrap">Your Business.</span></span>'
description: "We design, build and connect your website to the tools you already use, so small businesses, nonprofits and public organizations can grow with less busywork. We’ll be the busy bees."

button:
  # Refer to sharedButton in src/sections.schema.ts for all options.
  enable: true
  label: "Contact Us"
  url: "/contact/"

secondaryButton:
  # Refer to sharedButton in src/sections.schema.ts for all options.
  enable: true
  label: "View Our Work"
  url: "/portfolio/"
  variant: "outline"

# Optional small line under the buttons
# note: "From our New York hive to wherever you buzz. Local care, global reach."

# Browser mockup on the right of the hero.
# image: "/images/banner/client-site.jpg" # Optional screenshot (in src/assets/images). Without it a sample site is drawn.
# The sample site is a made-up local HVAC business; its photos live in src/assets/hero-mockup.
mockup:
  url: "northsideheating.com"
  siteName: "Northside Heating & Air"
  siteNav: ["Services", "Reviews", "Contact"]
  sitePhone: "(315) 555-0142"
  siteCallButton: "Call now"
  siteHeadline: "Fast, honest heating & AC repair"
  siteSubtitle: "Same-day service across Central NY"
  siteButton: "Book a visit"
  siteRating: "4.9 · 200+ Google reviews"
  siteServices: # One card per service; the photos are matched by position
    - name: "Furnace Repair"
      detail: "Same-day service"
    - name: "AC Installation"
      detail: "Free estimates"
    - name: "Maintenance Plans"
      detail: "from $89/yr"
  chatLabel: "AI receptionist"
  chatText: "Booked: Tue 3:00 PM — Furnace tune-up"
  notificationTitle: "New service request"
  notificationText: "Furnace repair · 2 min ago"
---
