<script lang="ts">
	import { Avatar } from '@skeletonlabs/skeleton';
	import type { ModalSettings } from '@skeletonlabs/skeleton';
	import { modalStore } from '@skeletonlabs/skeleton';
	import dayjs from 'dayjs';
	import duration from 'dayjs/plugin/duration';
	import { invalidateAll } from '$app/navigation';
	import type { JobType } from '../types/job.type';

	import IconRestart from '~icons/mdi/restart';

	export let job: JobType;

	let api_url = import.meta.env.VITE_API_URL;
	let s3_url = import.meta.env.VITE_S3_URL;

	$: status_class = () => {
		switch (job.status) {
			case 'COMPLETED':
				return 'variant-filled-success';
			case 'FAILED':
				return 'variant-filled-error';
			default:
				return 'variant-filled';
		}
	};

	dayjs.extend(duration);

	function modalImg(url: string): void {
		const d: ModalSettings = {
			title: 'Image details',
			image: url
		};
		modalStore.trigger(d);
	}

	async function retryJob() {
		await fetch(`${api_url}/job/${job.id}/retry`);
		invalidateAll();
	}
</script>

<div class="flex py-4 card">
	<div class="px-6 basis-1/3">
		<div>
			# {job.id}
			<span class="chip {status_class()}">{job.status}</span>
			<span class="flex-wrap">
				{#if job.status == 'COMPLETED'}
					{dayjs.duration(dayjs(job.finished_at).diff(dayjs(job.started_at))).format('m[m] s[s]')}
				{:else if job.status == 'FAILED'}
					{dayjs.duration(dayjs(job.finished_at).diff(dayjs(job.created_at))).format('m[m] s[s]')}
				{:else}
					{dayjs.duration(dayjs().diff(dayjs(job.created_at))).format('mm[m] ss[s]')}
				{/if}
			</span>
		</div>

		{#if job.status != 'COMPLETED' && job.status != 'PROCESSING'}
			<button type="button" class="my-4 btn variant-filled" on:click={() => retryJob()}>
				<IconRestart />
				<span>Retry</span>
			</button>
		{/if}

		<p>{JSON.stringify(job.process_params)}</p>
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
