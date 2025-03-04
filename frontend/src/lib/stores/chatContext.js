import { writable } from 'svelte/store';

// Default context: no intent at the start
export const chatContext = writable({
    intent: null
});
