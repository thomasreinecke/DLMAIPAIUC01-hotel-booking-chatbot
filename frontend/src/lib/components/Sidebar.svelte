<script>
  import { BedDouble } from 'lucide-svelte';
  import { chatContext } from "$lib/stores/chatContext.js"; // Import the chatbot context store

  let currentIntent = "None";
  chatContext.subscribe(value => {
    currentIntent = value.intent || "None";
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
    <p class="text-md font-semibold">Intent: {currentIntent}</p>
  </div>
</div>
