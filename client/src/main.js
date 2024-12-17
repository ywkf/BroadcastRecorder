// client/src/main.js
import { createApp } from 'vue';
import App from './App.vue'; // 引入 App.vue 作为根组件
import router from './router'; // 引入路由

const app = createApp(App);
app.use(router); // 使用 Vue Router
app.mount('#app'); // 挂载 Vue 应用
