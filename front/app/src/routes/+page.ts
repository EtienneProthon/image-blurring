import type { PageLoad } from './$types';

export const load = (async ({ fetch, depends }) => {
  let api_url = import.meta.env.VITE_API_URL;
  const res = await fetch(`${api_url}/job_groups?order=-id`);
  const items = await res.json();

  depends('app:job_groups');

  return { items };
}) satisfies PageLoad;
