<script lang="ts">
  import '../app.postcss';
  import '../global.css';
  import Sidebar from '$lib/components/Sidebar.svelte'; 
  import ChatWindow from '$lib/components/ChatWindow.svelte'; 
</script>

<div class="flex h-screen">
<Sidebar /> 
<div class="flex flex-col flex-1 bg-gray-100">
  <ChatWindow />
</div>
</div>
