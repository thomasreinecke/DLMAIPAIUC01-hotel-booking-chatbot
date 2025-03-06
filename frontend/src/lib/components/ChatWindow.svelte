<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import { writable, get } from "svelte/store";
  import ChatPost from "$lib/components/ChatPost.svelte";
  import { sessionId } from "$lib/stores/sessionStore.js";
  import { chatContext } from "$lib/stores/chatContext.js";
  
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  // Define types
  type Message = {
    text: string;
    sender: "user" | "bot";
  };

  // Svelte stores and local variables
  let messages = writable<Message[]>([]);
  let userInput = "";
  let messagesContainer: HTMLDivElement;
  let chatInput: HTMLInputElement; // Reference to the chat input
  let isScrolledToBottom = true;
  let messageAdded = false;
  let currentSessionId = "";

  // Subscribe to sessionId store
  sessionId.subscribe(value => {
    currentSessionId = value;
  });

  // Fetch chat history for the current session
  async function fetchMessages() {
    try {
      const response = await fetch(`${backendUrl}/chat/history?sessionId=${currentSessionId}`);
      const data = await response.json();
      messages.set(data.history);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }

  // Initial call to get the introduction greeting if no messages exist
  async function initChat() {
    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Send an empty message to trigger the backend to return the intro greeting
        body: JSON.stringify({ message: "", sessionId: currentSessionId })
      });
      const data = await response.json();
      console.log("Initial chat response:", data);
      messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
      chatContext.set(data.context);
    } catch (error) {
      console.error("Error initializing chat:", error);
    }
  }

  // Send a message to the backend and receive a response
  async function sendMessage() {
    if (!userInput.trim()) return;

    messageAdded = true;
    messages.update(msgs => [...msgs, { text: userInput, sender: "user" }]);
    
    const sentMessage = userInput;
    userInput = "";

    try {
      console.log(`Sending message with sessionId=${currentSessionId}`);
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: sentMessage, sessionId: currentSessionId })
      });
      const data = await response.json();
      console.log(data);
      messageAdded = true;
      messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
      chatContext.set(data.context);
    } catch (error) {
      console.error("Error sending message:", error);
    }
    // After sending, focus back on the chat input.
    chatInput.focus();
  }

  // Scroll the chat window to the bottom
  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  // Check if the user is scrolled to the bottom
  function checkScroll() {
    if (messagesContainer) {
      const distanceFromBottom = messagesContainer.scrollHeight - messagesContainer.clientHeight - messagesContainer.scrollTop;
      isScrolledToBottom = distanceFromBottom < 20;
    }
  }

  // Initial setup when component mounts
  onMount(async () => {
    await fetchMessages();
    if (get(messages).length === 0) {
      await initChat();
    }
    // Focus the chat input when the screen loads.
    chatInput.focus();
  });

  // Ensure smooth scrolling when messages are added
  afterUpdate(() => {
    if (messageAdded || isScrolledToBottom) {
      scrollToBottom();
      messageAdded = false;
    }
  });

  // Listen for scroll events to update the scroll state
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
      bind:this={chatInput}
      on:keyup={(e) => e.key === 'Enter' && sendMessage()}
    />
  </div>
</div>
