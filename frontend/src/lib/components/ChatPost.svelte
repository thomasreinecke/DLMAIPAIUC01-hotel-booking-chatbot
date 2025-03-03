<script>
  export let sender = "user"; // Defaults to user
  export let text = "";
</script>

<!-- Chat Message -->
<div class="p-3 rounded-md w-full
  {sender === 'bot' ? 'bg-gray-200 text-gray-900' : 'bg-primary text-black font-semibold'}">
  {text}
</div>
