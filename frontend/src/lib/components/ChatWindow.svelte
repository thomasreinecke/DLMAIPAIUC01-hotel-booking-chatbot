<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import { writable, get } from "svelte/store";
  import ChatPost from "$lib/components/ChatPost.svelte";
  import { sessionId } from "$lib/stores/sessionStore.js";
  import { chatContext } from "$lib/stores/chatContext.js";
  
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  type Message = {
    text: string;
    sender: "user" | "bot";
  };

  let messages = writable<Message[]>([]);
  let userInput = "";
  let messagesContainer: HTMLDivElement;
  let chatInput: HTMLInputElement;
  let isScrolledToBottom = true;
  let messageAdded = false;
  let currentSessionId = "";

  sessionId.subscribe(value => {
    currentSessionId = value;
  });

  async function fetchMessages() {
    try {
      const response = await fetch(`${backendUrl}/chat/history?sessionId=${currentSessionId}`);
      const data = await response.json();
      messages.set(data.history);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }

  async function initChat() {
    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "", sessionId: currentSessionId })
      });
      const data = await response.json();
      console.log("Initial chat response:", data);
      // If reset flag is returned, clear history and set only the bot reply.
      if (data.reset) {
        messages.set([{ text: data.reply, sender: "bot" }]);
      } else {
        messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
      }
      chatContext.set(data.context);
    } catch (error) {
      console.error("Error initializing chat:", error);
    }
  }

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
      // If backend signals a reset, clear history and show only the new bot reply.
      if (data.reset) {
        messages.set([{ text: data.reply, sender: "bot" }]);
      } else {
        messages.update(msgs => [...msgs, { text: data.reply, sender: "bot" }]);
      }
      chatContext.set(data.context);
    } catch (error) {
      console.error("Error sending message:", error);
    }
    chatInput.focus();
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  function checkScroll() {
    if (messagesContainer) {
      const distanceFromBottom = messagesContainer.scrollHeight - messagesContainer.clientHeight - messagesContainer.scrollTop;
      isScrolledToBottom = distanceFromBottom < 20;
    }
  }

  onMount(async () => {
    await fetchMessages();
    if (get(messages).length === 0) {
      await initChat();
    }
    chatInput.focus();
  });

  afterUpdate(() => {
    if (messageAdded || isScrolledToBottom) {
      scrollToBottom();
      messageAdded = false;
    }
  });

  function handleScroll() {
    checkScroll();
  }
</script>

<div class="flex flex-col h-screen">
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
