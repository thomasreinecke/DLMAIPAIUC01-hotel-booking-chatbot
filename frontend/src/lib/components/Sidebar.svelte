<script>
  import { BedDouble } from 'lucide-svelte';
  import { chatContext } from "$lib/stores/chatContext.js"; 

  let context = {};
  chatContext.subscribe(value => {
    context = value || {};
  });
</script>

<div class="w-64 bg-gray-800 text-white p-4 flex flex-col h-full sticky top-0">
  <div class="flex items-center space-x-3 mb-6">
    <BedDouble class="text-white text-3xl" />
    <h2 class="text-lg font-bold">Roomie</h2>
  </div>

  <div class="text-sm text-gray-300 mb-6">
    Use the chatbot to book a hotel room, change, or cancel an existing reservation.
  </div>

  <div class="mt-auto bg-gray-700 p-3 rounded-lg">
    <h3 class="text-sm text-gray-300">Context</h3>
    <p class="text-md font-semibold">Intent: {context.intent || "None"}</p>
    
    {#if context.data}
      <p class="text-sm text-gray-300">Guest Name: {context.data["guest name"] || "N/A"}</p>
      <p class="text-sm text-gray-300">Check-in: {context.data["check-in date"] || "N/A"}</p>
      <p class="text-sm text-gray-300">Check-out: {context.data["check-out date"] || "N/A"}</p>
      <p class="text-sm text-gray-300">Guests: {context.data["number of guests"] || "N/A"}</p>
      <p class="text-sm text-gray-300">Breakfast: {context.data["breakfast inclusion"] || "N/A"}</p>
      <p class="text-sm text-gray-300">Payment: {context.data["payment method"] || "N/A"}</p>
    {/if}
  </div>
</div>
