<script lang="ts">
	import { ProgressBar } from '@skeletonlabs/skeleton';
	import dayjs from 'dayjs';
	import duration from 'dayjs/plugin/duration';

	import IconAlert from '~icons/mdi/alert';
	import Job from './Job.svelte';

	export let job_group_id: string;

	let api_url = import.meta.env.VITE_API_URL;

	dayjs.extend(duration);

	async function getData() {
		const res = await fetch(`${api_url}/jobs?job_group_id=${job_group_id}`);
		const items = await res.json();
		return items;
	}
</script>

{#await getData()}
	<p>Fetching data...</p>
	<ProgressBar />
{:then items}
	{#each items as job}
		<Job {job} />
	{/each}
{:catch error}
	<aside class="alert variant-ghost">
		<!-- Icon -->
		<div>
			<IconAlert />
		</div>
		<!-- Message -->
		<div class="alert-message">
			<h3>Error</h3>
			<p>{error.message}</p>
		</div>
	</aside>
{/await}
