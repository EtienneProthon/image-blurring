import type { PageLoad } from './$types';

export const load = (async ({ fetch, depends }) => {
  let api_url = import.meta.env.VITE_API_URL;
  const res = await fetch(`${api_url}/job_groups?order=-id`);
  const items = await res.json();

  const need_refresh = items.some((e) => e.completed_jobs < e.total_jobs);

  console.log('Need refresh', need_refresh);
  depends('app:job_groups');

  return { items, need_refresh };
}) satisfies PageLoad;
