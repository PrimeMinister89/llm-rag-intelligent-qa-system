<template>
  <el-container class="container">
    <el-aside class="history">
      <el-tabs v-model="activeName" class="demo-tabs">
        <el-tab-pane label="问题记录" name="first">
          <el-button @click="start_new_conversation" type="success" round>开启新对话</el-button>
          <el-menu
          default-active="1"
          class="el-menu-vertical-demo"
          >
            <el-sub-menu v-for="(questions, index) in conversation" :key="index">
              <el-menu-item-group v-for="(item, index) in questions" :key="index" @click="() => handleClick(item)">
                <el-icon><document /></el-icon>
                {{ item }}
              </el-menu-item-group>
            </el-sub-menu>
          </el-menu>
        </el-tab-pane>
        <el-tab-pane label="文件信息" name="second">
          <ul>
            <li v-for="(item, index) in fileHistory" :key="index">
              {{ item }}
            </li>
          </ul>
        </el-tab-pane>
      </el-tabs>
    </el-aside>
    <el-main v-loading="loading" class="chat-box">
      <div class="showResponse">
        <h3>回复:</h3>
        <p>{{ reply }}</p>
        <!-- <p>{{ selectedFile }}</p> -->
        <!-- {{ QandA }} -->
        <!-- {{ isloadConversation }} -->
      </div>
      <div class="sendMessage">
        <div class="text">
          <textarea v-model="message" placeholder="请输入你的问题" rows="4"></textarea>
          <el-tooltip class="box-item" effect="dark" content="启用后，将调用工具辅助大模型生成回复" placement="top">
            <el-switch v-model="value1" active-text="启用代理" />
          </el-tooltip>
        </div>
        <div class="button-area">
            <el-row :gutter="20" justify="center">
              <el-button @click="sendMessage" type="primary" size="large" :icon="Search"
          style="width: 125px">Search</el-button>
            </el-row>
            <el-row :gutter="20" justify="center">
              <el-button @click="uploadFile = true" type="primary" size="large" :icon="Upload"
          style="width: 125px">Upload</el-button>
            </el-row>
            <el-row :gutter="20" justify="center">
              <el-button @click="cleanFile" type="primary" size="large" :icon="Delete" style="width: 125px">Clean</el-button>
            </el-row>
        </div>
      </div>
    </el-main>
  </el-container>

  <el-dialog v-model="uploadFile" width="1000">
    <el-upload class="upload-demo" drag :auto-upload="false" multiple :on-change="handleFileChange">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件至此处或者 <em>点击以上传文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持文本和图片文件
        </div>
      </template>
    </el-upload>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import axios from 'axios'
import { Delete, Edit, Search, Share, Upload } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import type { UploadRawFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import {Document} from '@element-plus/icons-vue'

const question = ref<string[]>([])
const fileHistory = ref<UploadFile[]>([])

const message = ref('')

const messageToSend = ref('')

const reply = ref('')
const show_file_info = ref<UploadFile | null>(null)
const value1 = ref(false)
const uploadFile = ref(false)
//用数组装载上传的文件，用作多文件RAG
const selectedFile = ref<Array<UploadRawFile | null>>([])
const activeName = ref('first')
const QandA = ref<Array<{ question: string, answer: string }>>([])

const conversation = ref<Array<string[]>>([])

const loading = ref(false)

const isloadConversation = ref(true)

const handleFileChange = (file:UploadFile) => {
  show_file_info.value = file
  if (file.raw !== undefined) {
    selectedFile.value.push(file.raw)
  } else {
    selectedFile.value.push(null)
  }
  uploadFile.value = false,
  fileHistory.value.push(show_file_info.value)
  ElMessage({
    message:"文件已成功上传",
    type:"success"
  })
}

const sendMessage = async () => {
  const formData = new FormData()
  formData.append("message", message.value)
  formData.append("value1", value1.value.toString())
  question.value.push(message.value)
  if (isloadConversation.value) {
    conversation.value.push(question.value)
    isloadConversation.value = false
  }
  messageToSend.value = message.value
  message.value = ''

  if (selectedFile.value.length>0) {
    selectedFile.value.forEach((file)=>{
      if (file){
        formData.append("files", file)
      }
    })
  }
  
  loading.value = true

  try {
    const res = await axios.post('http://localhost:8000/chat', formData)
    reply.value = res.data.reply
    QandA.value.push({ question: messageToSend.value, answer: res.data.reply })
    loading.value = false
  } catch (err) {
    reply.value = '请求失败，请检查服务器'
    loading.value = false
    console.error(err)
  }
}

const handleClick = (item:string) => {
  // ElMessage({
  //   message:"点击已被记录",
  //   type:"success"
  // })
  QandA.value.forEach((qa) => {
    if (qa.question === item) {
      reply.value = qa.answer
    }
  })
}

const cleanFile = () => {
  ElMessage({
    message:"文件待传缓冲区已清理",
    type:"success"
  })
  selectedFile.value = [],
  fileHistory.value = []
}

const start_new_conversation = async () =>{
  ElMessage({
    message:"新对话已创建",
    type:"success"
  })
  isloadConversation.value = true
  question.value = []
  await axios.post("http://localhost:8000/reset",{
    new_session:true
  })
}
</script>

<style scoped>
.container {
  position: fixed;
  inset: 0;
}

.history {
  width: 30%;
  height: 100%;
  background-color:floralwhite;
}

.chat-box {
  width: 70%;
  height: 100%;
}

.showResponse {
  position: relative;
  width: 100%;
  height: 70%;
}

.sendMessage {
  position: relative;
  width: 100%;
  height: 30%;
  display: flex;
}

.text {
  position: relative;
  width: 70%;
  height: 100%;
}

.button-area {
  position: relative;
  width: 30%;
  height: 100%;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

textarea {
  position: relative;
  width: 100%;
  height: 80%;
  border-radius: 10px;
  font-size: 20px;
}

.box-item {
  width: 110px;
  margin-top: 10px;
}

textarea::placeholder{
  font-size:20px;
  font-style:normal;
}

</style>