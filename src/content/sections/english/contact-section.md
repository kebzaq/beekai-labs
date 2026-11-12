---
# Contact section. Email, phone and service area come from `settings.contactInfo` in src/config/config.toml
enable: true
title: "Tell us about your project"
description: "Share a few details and we will come back with ideas and next steps."
note: "We reply within 1 business day."

# Check config.toml for the form provider settings
form:
  emailSubject: "New message from the website"
  submitButton:
    # Refer to sharedButton in src/sections.schema.ts for all options.
    enable: true
    label: "Send Message"
  inputs:
    - label: "Name"
      placeholder: "Your name"
      name: "Name" # The name this field arrives under
      required: true
      halfWidth: true
    - label: "Email"
      placeholder: "you@example.com"
      name: "Email"
      required: true
      type: "email"
      halfWidth: true
    - label: "Message"
      tag: "textarea"
      rows: "3"
      placeholder: "What would you like help with?"
      name: "Message"
      required: true
    - note: success # info | warning | success | deprecated | hint
      parentClass: "hidden text-sm message success"
      content: We have received your message. We reply within 1 business day.
    - note: deprecated
      parentClass: "hidden text-sm message error"
      content: Something went wrong. Please try again later or contact us by email.
---
