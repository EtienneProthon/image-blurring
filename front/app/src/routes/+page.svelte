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
	import JobList from '$lib/JobList.svelte';
	import ModalCreateProcess from '$lib/ModalCreateProcess.svelte';
	import dayjs from 'dayjs';
	import duration from 'dayjs/plugin/duration';
	import { invalidate } from '$app/navigation';

	export let data: PageData;
	let api_url = import.meta.env.VITE_API_URL;

	dayjs.extend(duration);

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
		<button type="button" class="btn variant-filled" on:click={modalProcess}>
			<span>Run Process</span>
			<IconSend />
		</button>
	</svelte:fragment>
</AppBar>
<div class="container flex items-center mx-auto">
	<Accordion class="flex-grow">
		{#each data.items as job_group}
			<AccordionItem>
				<svelte:fragment slot="lead">{job_group.id}</svelte:fragment>
				<svelte:fragment slot="summary">
					<div class="flex items-center">
						<span>{dayjs(job_group.created_at).format('DD/MM/YYYY - HH:mm:ss')}</span>
						<ProgressBar
							class="{job_group.completed_jobs < job_group.total_jobs
								? 'animate-pulse'
								: ''} shrink"
							value={job_group.completed_jobs}
							max={job_group.total_jobs}
						/>
						-
						<span>{job_group.completed_jobs}/{job_group.total_jobs}</span>
						-
						<span class="flex-wrap"
							>{dayjs
								.duration(dayjs(job_group.finished_at).diff(dayjs(job_group.created_at)))
								.format('mm:ss')}</span
						>
					</div>
				</svelte:fragment>
				<svelte:fragment slot="content"><JobList job_group_id={job_group.id} /></svelte:fragment>
			</AccordionItem>
		{/each}
	</Accordion>
</div>
<Modal />
