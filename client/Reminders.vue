<template>
  <v-container>
    <!-- 添加提醒事项 -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            添加提醒事项
          </v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submitReminder">
              <v-text-field v-model="title" label="标题" required></v-text-field>
              <v-textarea v-model="description" label="描述"></v-textarea>
              <v-menu
                v-model="menu"
                :close-on-content-click="false"
                :nudge-right="40"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="remindAt"
                    label="提醒时间"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    required
                  ></v-text-field>
                </template>
                <v-date-picker v-model="date" @input="saveDate">
                  <v-spacer></v-spacer>
                  <v-btn text color="primary" @click="menu = false">取消</v-btn>
                  <v-btn text color="primary" @click="saveDate">保存</v-btn>
                </v-date-picker>
              </v-menu>
              <v-btn type="submit" color="primary" class="mt-4">添加提醒</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 今日提醒事项 -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            今天的提醒事项
          </v-card-title>
          <v-card-text>
            <v-timeline>
              <v-timeline-item
                v-for="reminder in todayReminders"
                :key="reminder.id"
                :icon="getIcon(reminder)"
                small
              >
                <v-card>
                  <v-card-title>{{ reminder.title }}</v-card-title>
                  <v-card-text>
                    {{ reminder.description }}
                    <div class="text-right">{{ formatTime(reminder.remind_at) }}</div>
                    <!-- 删除按钮 -->
                    <v-btn @click="deleteReminder(reminder.id)" color="red" small>删除</v-btn>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 日历 -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            日历
          </v-card-title>
          <v-card-text>
            <vue-cal
              :events="calendarEvents"
              :time="false"
              :default-view="'month'"
              @event-click="onEventClick"
            ></vue-cal>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'

export default {
  components: {
    VueCal
  },
  data() {
    return {
      title: '',
      description: '',
      remindAt: '',
      date: null,
      menu: false,
      todayReminders: [],
      calendarEvents: []
    }
  },
  methods: {
    // 获取当天的提醒事项
    async fetchReminders() {
      try {
        const response = await axios.get('http://localhost:8000/api/reminders')
        const reminders = response.data
        const today = new Date().toISOString().split('T')[0]
        this.todayReminders = reminders.filter(r => r.remind_at.startsWith(today))
        this.calendarEvents = reminders.map(r => ({
          start: r.remind_at,
          end: r.remind_at,
          title: r.title,
          content: r.description
        }))
      } catch (error) {
        console.error("获取提醒事项失败:", error)
      }
    },

    // 提交新的提醒事项
    async submitReminder() {
      try {
        await axios.post('http://localhost:8000/api/reminders', {
          title: this.title,
          description: this.description,
          remind_at: this.remindAt
        })
        this.title = ''
        this.description = ''
        this.remindAt = ''
        this.fetchReminders() // 提交后刷新提醒事项
      } catch (error) {
        console.error("添加提醒事项失败:", error)
      }
    },

    // 保存选择的日期
    saveDate() {
      const selectedDate = new Date(this.date)
      const formattedDate = selectedDate.toISOString()
      this.remindAt = formattedDate
      this.menu = false
    },

    // 格式化时间
    formatTime(datetime) {
      const date = new Date(datetime)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },

    // 获取提醒事项图标
    getIcon(reminder) {
      return 'mdi-bell'
    },

    // 点击日历事件
    onEventClick(event) {
      alert(`提醒: ${event.title}\n描述: ${event.content}\n时间: ${event.start}`)
    },

    // 删除提醒事项
    async deleteReminder(id) {
      try {
        await axios.delete(`http://localhost:8000/api/reminders/${id}`)
        this.fetchReminders() // 删除后刷新提醒事项
      } catch (error) {
        console.error("删除提醒事项失败:", error)
      }
    }
  },

  // 页面加载时获取提醒事项
  mounted() {
    this.fetchReminders()
  }
}
</script>

<style scoped>
/* 样式定制 */
</style>
