// @ts-nocheck
import { markdownify } from "./textConverter";

/**
 * Resets the form by clearing all input values and removing any success or error classes.
 * It also resets the selected index of dropdowns and clears values for select tags.
 */

export function formReset(form: HTMLFormElement) {
  form?.reset();

  const validationTags = form?.querySelectorAll(
    "[input-wrapper]:not(.hidden):not(.message).success, [input-wrapper]:not(.hidden):not(.message).error",
  );

  validationTags?.forEach((tag) => {
    tag.classList.remove("success", "error");
  });

  const selectTags = form?.querySelectorAll(
    "[input-wrapper]:not(.hidden) select[data-hs-select]",
  );

  selectTags?.forEach((tag) => {
    const selectElement = tag as HTMLSelectElement;
    const select = window.HSSelect.getInstance(tag);
    selectElement.selectedIndex = 0;

    if (select) {
      select.setValue("");
    }
  });
}

/**
 * Validates a select element by adding 'success' or 'error' classes
 * based on whether the selection has a value.
 *
 * @param tag - The HTMLSelectElement to validate.
 */
export const validateSelectTag = (tag: HTMLSelectElement) => {
  const validationTag = tag.closest("[input-wrapper]");

  if (tag.value === "") {
    validationTag?.classList.add("error");
    validationTag?.classList.remove("success");
  } else {
    validationTag?.classList.contains("error") &&
      validationTag?.classList.add("success");
    validationTag?.classList.remove("error");
  }
};

/**
 * Checks if all required fields in a form have values.
 *
 * @param form - The form element to check.
 * @returns true if all required fields have values, false otherwise.
 */
export function isFormFilled(form: HTMLFormElement): boolean {
  const elements = form.querySelectorAll(
    "input[name], [input-wrapper]:not(.hidden) select[data-hs-select], textarea[name]",
  );
  type element = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;

  // Check if all required fields have values
  for (let element of elements) {
    const elem = element as element;

    if (elem.tagName === "SELECT" && elem.value === "") {
      return false;
    } else if (elem.hasAttribute("required") && elem.value === "") {
      return false;
    }
  }
  return true;
}

/**
 * Displays a message in the form's message area based on success or error status.
 * Optionally disables the submit button.
 *
 * @param message - The message to display.
 * @param success - Whether the message is a success or error message.
 * @param disableSubmit - Optionally disables the submit button if true.
 * @param form - form element
 */
export const setMessage = (
  message: string,
  success: boolean,
  disableSubmit = false,
  form: HTMLFormElement,
) => {
  const submitButton = form?.querySelector('button[type="submit"]');
  const messageType = success ? "success" : "error";
  const allMessages = form.querySelectorAll(".message");
  const messageElement = form.querySelector(`.message.${messageType}`);
  const msgEleText = messageElement?.querySelector(".prose-styles");
  const default_message = msgEleText?.getAttribute("data-default");

  // Hide all messages before showing the selected one
  allMessages.forEach((msg) => {
    if (msg !== messageElement) {
      msg.classList.add("hidden");
    }
  });

  if (message === "default" && msgEleText && default_message) {
    msgEleText.innerHTML = markdownify(default_message, true) as string;
  }

  // Show the selected message
  messageElement?.classList.remove("hidden");

  // Disable or enable submit button based on 'disableSubmit'
  if (disableSubmit) {
    submitButton?.setAttribute("disabled", "true");
  } else {
    submitButton?.removeAttribute("disabled");
  }

  if (msgEleText && message !== "default") {
    msgEleText.innerHTML = markdownify(message, true) as string;
  }
};

/**
 * Sends a POST request with a specified timeout and aborts if the timeout is exceeded.
 *
 * @param url - The URL to send the request to.
 * @param data - The form data to send.
 * @param controller - An AbortController to manage request timeout.
 * @param timeout - The timeout duration in milliseconds.
 */
export const fetchWithTimeout = async (
  url: string,
  data: Record<string, FormDataEntryValue>,
  controller: AbortController,
  timeout: number,
) => {
  setTimeout(() => controller.abort(), timeout);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(data),
    signal: controller.signal,
  });

  if (response.status !== 200) {
    throw new Error("Request failed with status code " + response.status);
  }
};

/**
 * Submits form data to the configured Formspree endpoint.
 *
 * @param action - The Formspree form endpoint from `contactFormAction`, e.g. https://formspree.io/f/your_form_id.
 * @param data - The form data to submit.
 * @param timeout - The timeout duration in milliseconds for the request.
 */
export const formspreeSubmit = async (
  action: string,
  data: Record<string, FormDataEntryValue>,
  timeout: number,
  form: HTMLFormElement,
) => {
  try {
    await fetchWithTimeout(action, data, new AbortController(), timeout);
    setMessage("default", true, false, form);
    formReset(form);
  } catch (error) {
    setMessage(
      error + "! Please try again later or contact us by email.",
      false,
      false,
      form,
    );
  }
};

/**
 * Submits the form to Netlify Forms with fetch, so the visitor stays on the page.
 * Shows the success message and resets the form, or shows the error message.
 * Returns true only when Netlify confirmed the submission.
 *
 * @param form - The form element (must include the hidden "form-name" field).
 * @param action - Where to POST, "/" for Netlify Forms.
 * @param timeout - Milliseconds before giving up (default 15 seconds).
 */
export const netlifySubmit = async (
  form: HTMLFormElement,
  action = "/",
  timeout = 15000,
): Promise<boolean> => {
  // Netlify Forms takes a URL-encoded POST that includes the hidden "form-name" field
  const data = new URLSearchParams(new FormData(form) as any).toString();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(action, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: data,
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new Error(`Netlify Forms answered with status ${response.status}`);
    }
    setMessage("default", true, false, form);
    formReset(form);
    return true;
  } catch (error) {
    console.error("[contact form]", error);
    const timedOut = (error as Error).name === "AbortError";
    setMessage(
      timedOut
        ? "The request took too long. Please try again, or contact us by email."
        : "default", // The form's own error message
      false,
      false,
      form,
    );
    return false;
  } finally {
    clearTimeout(timer);
  }
};
