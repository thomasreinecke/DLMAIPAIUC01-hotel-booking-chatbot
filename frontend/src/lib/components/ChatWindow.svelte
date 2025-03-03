<script>
  import { onMount } from "svelte";
  import { writable } from "svelte/store";
  import ChatPost from "$lib/components/ChatPost.svelte";

  let messages = writable([]);
  let userInput = "";

  async function fetchMessages() {
    try {
      const response = await fetch("http://127.0.0.1:8000/chat/history");
      const data = await response.json();
      messages.set(data.history);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }

  async function sendMessage() {
    if (!userInput.trim()) return;

    messages.update(msgs => [...msgs, { text: userInput, sender: "user" }]);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
      });

      const data = await response.json();
      messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
    } catch (error) {
      console.error("Error sending message:", error);
    }

    userInput = "";
  }

  onMount(fetchMessages);
</script>

<!-- Chat Window -->
<div class="flex flex-col flex-1 p-4 space-y-4 bg-background rounded-lg shadow-lg">
  <div class="flex-1 overflow-auto flex flex-col space-y-2">
    {#each $messages as message}
      <ChatPost sender={message.sender} text={message.text} />
    {/each}
  </div>

  <!-- Input Box -->
  <div class="p-4 border-t">
    <input 
      class="input w-full" 
      title="Chat Input" 
      type="text" 
      placeholder="Type your message..." 
      bind:value={userInput} 
      on:keyup={(e) => e.key === 'Enter' && sendMessage()}
    />
  </div>
</div>
