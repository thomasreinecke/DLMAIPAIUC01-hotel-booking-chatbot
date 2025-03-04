import { writable } from 'svelte/store';
import { v4 as uuidv4 } from 'uuid';
import { browser } from "$app/environment"; 

let storedSessionId = "";

// Only access localStorage in the browser (not during SSR)
if (browser) {
    storedSessionId = localStorage.getItem("sessionId") || uuidv4();
    localStorage.setItem("sessionId", storedSessionId);
}

// Create a writable store for session ID
export const sessionId = writable(storedSessionId);
