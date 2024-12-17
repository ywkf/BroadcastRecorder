// client/src/router/index.js

import Vue from 'vue'
import { createRouter, createWebHistory } from 'vue-router';  // 正确引入 Vue Router
import Reminders from '../../Reminders.vue';  // 这是正确的相对路径


const routes = [
  {
    path: '/',
    name: 'Reminders',
    component: Reminders,  // 配置路由与组件
  },
  // 其他路由配置
];

// 创建并导出路由实例
const router = createRouter({
  history: createWebHistory(),  // 使用 HTML5 History 模式
  routes,  // 路由配置
});

export default router;