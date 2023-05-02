<!-- YOU CAN DELETE EVERYTHING IN THIS PAGE -->
<script lang="ts">
	import {
		Modal,
		modalStore,
		AppBar,
		Accordion,
		ProgressBar,
		AccordionItem
	} from '@skeletonlabs/skeleton';
	import type { ModalSettings, ModalComponent } from '@skeletonlabs/skeleton';
	import IconRocket from '~icons/mdi/rocket-launch-outline';
	import IconSend from '~icons/mdi/send';
	import IconRefresh from '~icons/mdi/refresh';
	import JobList from '$lib/JobList.svelte';
	import ModalCreateProcess from '$lib/ModalCreateProcess.svelte';
	import dayjs from 'dayjs';
	import duration from 'dayjs/plugin/duration';
	import { invalidate, invalidateAll } from '$app/navigation';

	export let data: PageData;
	let api_url = import.meta.env.VITE_API_URL;

	// let clear;
	// $: {
	// 	clearInterval(clear);
	// 	if (data.need_refresh) {
	// 		clear = setInterval(() => invalidateAll(), 10000);
	// 	}
	// }

	dayjs.extend(duration);

	function refresh(): void {
		invalidate('app:job_groups');
	}

	const modalComponent: ModalComponent = {
		// Pass a reference to your custom component
		ref: ModalCreateProcess,
		// Add the component properties as key/value pairs
		props: { background: 'bg-red-500' },
		// Provide a template literal for the default component slot
		slot: '<p>Skeleton</p>'
	};

	function modalProcess(): void {
		const d: ModalSettings = {
			type: 'component',
			body: 'Complete the form below and then press submit.',
			component: modalComponent,
			title: 'Process Parameters',
			response: async (r: any) => {
				await fetch(`${api_url}/process_images`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json;charset=utf-8'
					},
					body: r.params
				});
				invalidate('app:job_groups');
			}
		};
		modalStore.trigger(d);
	}
</script>

<AppBar class="bg-gradient-to-br from-secondary-500 to-error-500">
	<svelte:fragment slot="lead"><IconRocket /></svelte:fragment>
	<h2>Image Processing</h2>
	<svelte:fragment slot="trail">
		<button type="button" class="btn variant-filled" on:click={refresh}>
			<IconRefresh />
		</button>
		<button type="button" class="btn variant-filled" on:click={modalProcess}>
			<span>Run Process</span>
			<IconSend />
		</button>
	</svelte:fragment>
</AppBar>
<div class="container flex overflow-auto items-center mx-auto">
	<Accordion class="flex-grow">
		{#each data.items as job_group}
			<AccordionItem>
				<svelte:fragment slot="lead">{job_group.id}</svelte:fragment>
				<svelte:fragment slot="summary">
					<div class="flex flex-row items-center text-center">
						<div class="basis-1/5">
							{dayjs(job_group.created_at).format('DD/MM/YYYY - HH:mm:ss')}
						</div>
						<ProgressBar
							class="{job_group.completed_jobs < job_group.total_jobs
								? 'animate-pulse'
								: ''} basis-2/5 shrink"
							value={job_group.completed_jobs}
							max={job_group.total_jobs}
						/>
						<div class="basis-1/5">{job_group.completed_jobs}/{job_group.total_jobs}</div>
						<div class="basis-1/5">
							{dayjs
								.duration(dayjs(job_group.finished_at).diff(dayjs(job_group.created_at)))
								.format('mm[m] ss[s]')}
						</div>
					</div>
				</svelte:fragment>
				<svelte:fragment slot="content"><JobList job_group_id={job_group.id} /></svelte:fragment>
			</AccordionItem>
		{/each}
	</Accordion>
</div>
<Modal />
