<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import { writable } from "svelte/store";
  import ChatPost from "$lib/components/ChatPost.svelte";
  import { sessionId } from "$lib/stores/sessionStore.js";
  import { chatContext } from "$lib/stores/chatContext.js"; // Import context store
  
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
  let currentSessionId = "";

  // Ensure sessionId is correctly retrieved (since it's not writable)
  sessionId.subscribe(value => {
    currentSessionId = value;
  });

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
      
      messageAdded = true;
      
      messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);

      // Store updated context in chatContext
      chatContext.set(data.context);
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

  // Ensure smooth scrolling when messages are added
  afterUpdate(() => {
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
