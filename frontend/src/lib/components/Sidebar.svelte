<script>
  import { BedDouble } from 'lucide-svelte';
  import { chatContext } from "$lib/stores/chatContext.js"; 

  let context = {};
  chatContext.subscribe(value => {
    context = value || {};
  });

  // Helper function to display a dash if a value is null or empty
  function displayOrDash(value) {
    return value !== null && value !== undefined && value !== "" ? value : "-";
  }
</script>

<div class="w-80 bg-gray-800 text-white p-4 flex flex-col h-full sticky top-0">
  <div class="flex items-center space-x-3 mb-6">
    <BedDouble class="text-white text-3xl" />
    <h2 class="text-lg font-bold">Roomie</h2>
  </div>

  <div class="text-sm text-gray-300 mb-6 font-semibold">
    The hotel booking assistant for Quantum Suites Hotel
  </div>

  <div class="text-sm text-gray-300 mb-6">
    Use the chatbot to book a hotel room, change, or cancel an existing reservation.
  </div>

  <div class="mt-auto rounded-lg overflow-hidden">
    <!-- Context header with Intent, Booking Number, Status and Language -->
    <div class="bg-gray-700 p-2 space-y-1">
      <div class="flex justify-between items-center">
        <span class="text-xs font-semibold">Booking number:</span>
        <span class="text-xs">
          {context.data && context.data["booking number"]
            ? context.data["booking number"]
            : "-"}
        </span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-xs font-semibold">Intent:</span>
        <span class="text-xs">{displayOrDash(context.intent)}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-xs font-semibold">Status:</span>
        <span class="text-xs">{displayOrDash(context.status)}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-xs font-semibold">Language:</span>
        <span class="text-xs">
          {context.data && context.data["language"]
            ? context.data["language"]
            : "-"}
        </span>
      </div>
    </div>
    
    <!-- Context table always shown -->
    <div class="bg-gray-600 p-2 mt-2">
      <table class="w-full text-sm">
        <tr>
          <td class="w-6">
            {context.data && context.data["guest name"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Guest Name</td>
          <td class="pl-2 text-right">
            {context.data ? displayOrDash(context.data["guest name"]) : "-"}
          </td>
        </tr>
        <tr>
          <td class="w-6">
            {context.data && context.data["check-in date"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Check-in</td>
          <td class="pl-2 text-right">
            {context.data ? displayOrDash(context.data["check-in date"]) : "-"}
          </td>
        </tr>
        <tr>
          <td class="w-6">
            {context.data && context.data["check-out date"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Check-out</td>
          <td class="pl-2 text-right">
            {context.data ? displayOrDash(context.data["check-out date"]) : "-"}
          </td>
        </tr>
        <tr>
          <td class="w-6">
            {context.data && context.data["number of guests"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Guests</td>
          <td class="pl-2 text-right">
            {context.data ? displayOrDash(context.data["number of guests"]) : "-"}
          </td>
        </tr>
        <tr>
          <td class="w-6">
            {context.data && context.data["breakfast inclusion"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Breakfast</td>
          <td class="pl-2 text-right">
            {context.data
              ? displayOrDash(context.data["breakfast inclusion"])
              : "-"}
          </td>
        </tr>
        <tr>
          <td class="w-6">
            {context.data && context.data["payment method"] ? "✅" : "❌"}
          </td>
          <td class="pl-2">Payment</td>
          <td class="pl-2 text-right">
            {context.data ? displayOrDash(context.data["payment method"]) : "-"}
          </td>
        </tr>
      </table>
    </div>
  </div>
</div>
