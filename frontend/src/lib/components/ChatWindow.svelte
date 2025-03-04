<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import { writable } from "svelte/store";
  import ChatPost from "$lib/components/ChatPost.svelte";
  
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  // Define types
  type Message = {
    text: string;
    sender: "user" | "bot";
  };

  // Define typed variables
  let messages = writable<Message[]>([]);
  let userInput = "";
  let messagesContainer: HTMLDivElement;
  let isScrolledToBottom = true;
  let messageAdded = false;

  // Fetch previous messages from the backend
  async function fetchMessages() {
    try {
      const response = await fetch(`${backendUrl}/chat/history`);
      const data = await response.json();
      messages.set(data.history);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }

  // Send a message to the backend and receive a response
  async function sendMessage() {
    if (!userInput.trim()) return;

    // Force scroll to bottom when adding user message
    messageAdded = true;
    
    // Add the user's message to the chat immediately (optimistic UI)
    messages.update(msgs => [...msgs, { text: userInput, sender: "user" }]);
    
    // Save current input and clear the field
    const sentMessage = userInput;
    userInput = "";

    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: sentMessage })
      });

      const data = await response.json();
      
      // Flag that a new message is being added (bot response)
      messageAdded = true;
      
      // Add bot's response to the chat
      messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  }

  // Scroll the chat window to the bottom
  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  // Check if user is scrolled to bottom before adding new messages
  function checkScroll() {
    if (messagesContainer) {
      const distanceFromBottom = 
        messagesContainer.scrollHeight - messagesContainer.clientHeight - messagesContainer.scrollTop;
      isScrolledToBottom = distanceFromBottom < 20;
    }
  }

  // Initial setup when component mounts
  onMount(() => {
    fetchMessages();
  });

  // Run after the DOM updates - perfect for scrolling after content changes
  afterUpdate(() => {
    // If a new message was added OR user was already at bottom, scroll to bottom
    if (messageAdded || isScrolledToBottom) {
      scrollToBottom();
      messageAdded = false;
    }
  });

  // Listen for scroll events to track if user has scrolled away from bottom
  function handleScroll() {
    checkScroll();
  }
</script>

<!-- Chat Window -->
<div class="flex flex-col h-screen">
  <!-- Chat Messages Container (Scrollable) -->
  <div 
    bind:this={messagesContainer} 
    class="flex-1 overflow-auto p-4 space-y-4 bg-white rounded-lg"
    on:scroll={handleScroll}
  >
    <div class="space-y-2">
      {#each $messages as message}
        <ChatPost sender={message.sender} text={message.text} />
      {/each}
    </div>
  </div>

  <!-- Input Box (Sticky at the bottom) -->
  <div class="sticky bottom-0 p-4 bg-white z-10 w-full border-t">
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