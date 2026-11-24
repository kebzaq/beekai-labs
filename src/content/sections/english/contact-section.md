---
# Contact section (Contact page and homepage): contact form and free preview request in one.
# Email, phone and service area come from `settings.contactInfo` in src/config/config.toml
enable: true
eyebrow: "Get in touch"
title: "Get a free preview of your new website"
description: "Share your current website or social media and we'll design a concept of your new homepage, free. Or just ask us anything."
note: "We reply within 1 business day."
secondaryNote: "No contracts, no pressure. Just a look at what's possible."

# Check config.toml for the form provider settings
form:
  # {name} is replaced with the Name field when the form is sent
  emailSubject: "New free preview request from {name}"
  submitButton:
    # Refer to sharedButton in src/sections.schema.ts for all options.
    enable: true
    label: "Get My Free Preview"
  inputs:
    - label: "Name"
      placeholder: "Your name"
      name: "name" # The name this field arrives under
      required: true
    - label: "Email"
      placeholder: "you@example.com"
      name: "email"
      required: true
      type: "email"
      halfWidth: true
    # Optional, any format (no validation), so it never blocks sending
    - label: "Phone"
      placeholder: "(XXX) XXX-XXXX"
      name: "phone"
      type: "tel"
      autocomplete: "tel"
      halfWidth: true
    - label: "Your website or social media"
      placeholder: "yourbusiness.com, Instagram or Facebook link"
      name: "links"
    - label: "Message"
      tag: "textarea"
      rows: "3"
      placeholder: "Tell us a bit about your business"
      name: "message"
      required: true
    - note: success # info | warning | success | deprecated | hint
      parentClass: "hidden text-sm message success"
      content: Thanks! We got your details and will get back to you within 1 business day.
    - note: deprecated
      parentClass: "hidden text-sm message error"
      content: Something went wrong. Please try again later or contact us by email.

  # Panel that replaces the form after a successful submission
  thankYou:
    title: "Thank you!"
    text: "Your message was sent successfully. We'll review your details and get back to you within 1 business day."
    linksText: "We'll take a look at your current site and social pages to prepare your free preview." # Only when a website/social link was shared
    nextTitle: "What happens next"
    nextSteps:
      - "We review your business and current website."
      - "We reach out to discuss what you need."
      - "You get a free homepage concept, with no commitment."
    primaryButton:
      enable: true
      label: "View Our Work"
      url: "/portfolio/"
    secondaryButton:
      enable: true
      label: "Back to Home"
      url: "/"
    resetLabel: "Send another message"
---
