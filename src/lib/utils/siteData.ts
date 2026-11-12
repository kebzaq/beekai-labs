import { getCollection } from "astro:content";

type OrderedCollection =
  | "serviceGroups"
  | "industries"
  | "portfolioCategories"
  | "process"
  | "whyUs"
  | "pricing"
  | "tools"
  | "stats"
  | "services";

// Entries of a data file (src/content/data/*.yml) in display order
const getOrdered = async <C extends OrderedCollection>(collection: C) =>
  (await getCollection(collection)).sort((a, b) => a.data.order - b.data.order);

export const getServiceGroups = () => getOrdered("serviceGroups");
export const getIndustries = () => getOrdered("industries");
export const getPortfolioCategories = () => getOrdered("portfolioCategories");
export const getProcessSteps = () => getOrdered("process");
export const getWhyUsItems = () => getOrdered("whyUs");
export const getPricingBlocks = () => getOrdered("pricing");
export const getTools = () => getOrdered("tools");
export const getStats = () => getOrdered("stats");

// Services in display order (src/content/data/services.yml)
export const getServices = () => getOrdered("services");

// Services of one group, in file order
export const getServicesByGroup = async (groupId: string) =>
  (await getServices()).filter((service) => service.data.group === groupId);
