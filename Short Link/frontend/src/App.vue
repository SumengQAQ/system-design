<template>
  <v-container>
    <v-text-field v-model="longUrl" label="长链接" variant="outlined" />
    <v-text-field v-model="customCode" label="自定义短码" variant="outlined" />
    <v-btn color="primary" @click="generate">生成短链接</v-btn>

    <v-alert v-if="error" type="error" :text="error" />
    <div v-if="shortUrl">
      <v-chip>{{ shortUrl }}</v-chip>
      <v-btn color="success" @click="copy">复制</v-btn>
    </div>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

// 响应式数据（变量变化时，页面自动更新）
const longUrl = ref('') // 长链接
const customCode = ref('') // 自定义短码
const shortUrl = ref('') // 生成的短链接
const error = ref('') // 错误信息

// 生成短链接的方法
const generate = async () => {
  // 清空上次的结果
  error.value = ''
  shortUrl.value = ''

  // 构建请求体
  const body = { long_url: longUrl.value }
  if (customCode.value.trim()) {
    body.custom_code = customCode.value.trim()
  }

  try {
    // 调用后端 API
    const response = await fetch('http://localhost:8000/encode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    // 如果响应状态不是 2xx，抛出错误
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '生成失败')
    }

    // 解析响应数据
    const data = await response.json()
    shortUrl.value = data.short_url
  } catch (e) {
    error.value = e.message
  }
}

// 复制到剪贴板
const copy = async () => {
  await navigator.clipboard.writeText(shortUrl.value)
  alert('已复制到剪贴板！')
}
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  font-family: sans-serif;
}

input,
button {
  margin: 8px 0;
  padding: 10px;
  width: 100%;
}

button {
  background-color: #42b883;
  color: white;
  border: none;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
}

.result {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.error {
  color: red;
}
</style>
