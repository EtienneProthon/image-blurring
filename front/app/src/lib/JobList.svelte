<script lang="ts">
	import { Avatar, ProgressBar } from '@skeletonlabs/skeleton';
	import type { ModalSettings } from '@skeletonlabs/skeleton';
	import { modalStore } from '@skeletonlabs/skeleton';
	import dayjs from 'dayjs';
	import duration from 'dayjs/plugin/duration';

	import IconAlert from '~icons/mdi/alert';

	export let job_group_id: string;

	let api_url = import.meta.env.VITE_API_URL;
	let s3_url = import.meta.env.VITE_S3_URL;

	dayjs.extend(duration);

	async function getData() {
		const res = await fetch(`${api_url}/jobs?job_group_id=${job_group_id}`);
		const items = await res.json();
		return items;
	}

	function modalImg(url: string): void {
		const d: ModalSettings = {
			title: 'Image details',
			image: url
		};
		modalStore.trigger(d);
	}
</script>

{#await getData()}
	<p>Fetching data...</p>
	<ProgressBar />
{:then items}
	{#each items as job}
		<div class="flex py-4 card">
			<div class="px-6 basis-1/3">
				<p># {job.id}</p>
				<span class="chip variant-filled">{job.status}</span>
				<span class="flex-wrap">
					{dayjs.duration(dayjs(job.finished_at).diff(dayjs(job.started_at))).format('mm:ss')}
				</span>
			</div>
			<div class="basis-1/3">
				<Avatar
					src={job.image_url}
					width="w-32"
					rounded="rounded-none"
					on:click={() => modalImg(job.image_url)}
				/>
			</div>
			<div class="basis-1/3">
				{#if job.status == 'COMPLETED'}
					<Avatar
						src="{s3_url}/{job.processed_image_s3}"
						width="w-32"
						rounded="rounded-none"
						on:click={() => modalImg(`${s3_url}/${job.processed_image_s3}`)}
					/>
				{:else}
					<div class="w-32 animate-pulse placeholder-circle" />
				{/if}
			</div>
		</div>
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
