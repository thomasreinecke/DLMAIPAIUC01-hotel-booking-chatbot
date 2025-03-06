<script>
  import { BedDouble } from 'lucide-svelte';
  import { chatContext } from "$lib/stores/chatContext.js"; 

  let context = {};
  chatContext.subscribe(value => {
    context = value || {};
  });
</script>

<div class="w-80 bg-gray-800 text-white p-4 flex flex-col h-full sticky top-0">
  <div class="flex items-center space-x-3 mb-6">
    <BedDouble class="text-white text-3xl" />
    <h2 class="text-lg font-bold">Roomie</h2>
  </div>

  <div class="text-sm text-gray-300 mb-6">
    Use the chatbot to book a hotel room, change, or cancel an existing reservation.
  </div>

  <div class="mt-auto rounded-lg overflow-hidden">
    <!-- Context header: Intent and Booking Number -->
    <div class="bg-gray-700 p-2">
      <h3 class="text-sm text-gray-300 font-semibold">Intent: {context.intent || "None"}</h3>
      <h4 class="text-xs text-gray-300">
        Booking #: {context.data && context.data["booking number"] ? context.data["booking number"] : "-"}
      </h4>
    </div>
    
    <!-- Context table always shown -->
    <div class="bg-gray-600 p-2">
      <table class="w-full text-sm">
        <tr>
          <td class="w-6">{context.data && context.data["guest name"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Guest Name</td>
          <td class="pl-2">{context.data ? context.data["guest name"] : ""}</td>
        </tr>
        <tr>
          <td class="w-6">{context.data && context.data["check-in date"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Check-in</td>
          <td class="pl-2">{context.data ? context.data["check-in date"] : ""}</td>
        </tr>
        <tr>
          <td class="w-6">{context.data && context.data["check-out date"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Check-out</td>
          <td class="pl-2">{context.data ? context.data["check-out date"] : ""}</td>
        </tr>
        <tr>
          <td class="w-6">{context.data && context.data["number of guests"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Guests</td>
          <td class="pl-2">{context.data ? context.data["number of guests"] : ""}</td>
        </tr>
        <tr>
          <td class="w-6">{context.data && context.data["breakfast inclusion"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Breakfast</td>
          <td class="pl-2">{context.data ? context.data["breakfast inclusion"] : ""}</td>
        </tr>
        <tr>
          <td class="w-6">{context.data && context.data["payment method"] !== null ? "✅" : "❌"}</td>
          <td class="pl-2">Payment</td>
          <td class="pl-2">{context.data ? context.data["payment method"] : ""}</td>
        </tr>
      </table>
    </div>
  </div>
</div>
