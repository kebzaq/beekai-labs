import rss from "@astrojs/rss";
import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import config from ".astro/config.generated.json";
import languages from "@/config/language.json";
import trailingSlashChecker from "@/lib/utils/trailingSlashChecker";

// RSS feed of published blog posts (drafts are left out)
export const GET: APIRoute = async (context) => {
  const { defaultLanguage } = config.settings.multilingual;
  const contentDir =
    languages.find((lang) => lang.languageCode === defaultLanguage)
      ?.contentDir || "english";

  const posts = (
    await getCollection(
      "blog",
      ({ id, data }) => id.startsWith(contentDir) && !data.draft,
    )
  ).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

  return rss({
    title: `${config.site.title} Blog`,
    description: config.site.description,
    site: context.site as URL,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      author: post.data.author,
      categories: post.data.tags,
      link: trailingSlashChecker(
        `/${config.settings.blogFolder}/${post.id.split("/").pop()?.replace(/\.mdx?$/, "")}`,
      ),
    })),
  });
};
