<script setup>
import axios from "axios";
import {ref, onMounted} from 'vue'

const emit = defineEmits(["getRecord"])
const props = defineProps(['isupstate'])
const color = {
  [0]: "舌色：淡白舌",
  [1]: "舌色：淡红舌",
  [2]: "舌色：红舌",
  [3]: "舌色：绛舌",
  [4]: "舌色：青紫舌",
}
const outcolor = {
  [0]: "舌苔颜色：白苔",
  [1]: "舌苔颜色：黄苔",
  [2]: "舌苔颜色：灰黑苔",
}
const rot = {
  [0]: "舌苔腻",
  [1]: "舌苔腐",
}
const thick = {
  [0]: "舌头薄",
  [1]: "舌头厚",
}

function reverseArray1(arr) {
  for (let index = 0; index < Math.floor(arr.length / 2); index++) {
    let temp = arr[index];
    arr[index] = arr[arr.length - 1 - index];
    arr[arr.length - 1 - index] = temp
  }
  return arr;
}

let rec = ref([0]);
let isEmpty = ref(false)

onMounted(function () {
  axios.get("/user/record", {
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
  }).then(res => {
    rec.value = res.data.data
    console.log(rec.value)
    if (Object.keys(rec.value).length !== 0) {
      console.log('rec is not null')
      isEmpty.value = true
      reverseArray1(rec.value)
    }
  }).catch(error => {
    console.log(error);
  })
})

onMounted(function () {
  const timer = window.setInterval(() => {
    setTimeout(function () {
      console.log(("开始轮询"))
      console.log(props.isupstate)
      if (props.isupstate === true || rec.value[0].state === 0) {
        console.log(("开始轮询加上向后端发送请求"))
        axios.get("/user/record", {
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
          }
        })
            .then(function (res) {
              console.log(res.data)
              rec.value = res.data.data
              reverseArray1(rec.value)
              console.log(rec.value)
              console.log(rec.value[0].state)
              if (Object.keys(rec.value).length !== 0) {
                console.log('rec is not null')
                isEmpty.value = true
              }
            })
            .catch(function (error) {
              console.log(error);
            })
            .then(res => {
              if (rec.value[0].state !== 0 || rec.value === []) {
                console.log("轮询停止")
                emit("getRecord", false)
              }
            })
      }
    }, 0)
  }, 2000)
});
</script>

<template>
  <div v-if="isEmpty === true" class="results-container">
    <div class="card panel-surface" v-for="item in rec" :key="item.id || item.img_src">
      <div class="result-header">
        <h3>Result</h3>
      </div>
      
      <div class="result-grid">
        <div class="result-item img-col">
          <div class="label">图片</div>
          <div class="value">
            <a :href="item.img_src" target="_blank" class="tag-link">click to view</a>
          </div>
        </div>
        
        <div class="result-item text-col">
          <div class="label">检测结果</div>
          <div class="value">
            <span v-if="item.state === 0" class="text-pending">
              Please wait while the test is being conducted.
            </span>
            <span v-if="item.state === 1" class="text-success">
              {{ color[item.result.tongue_color] }} {{ outcolor[item.result.coating_color] }} {{ rot[item.result.rot_greasy] }} {{ thick[item.result.tongue_thickness] }}
            </span>
            <span v-if="item.state === 201" class="text-error">
              No tongue image was detected. Please re-upload a clear tongue image.
            </span>
            <span v-if="item.state === 202" class="text-error">
              There are multiple tongue images, please take new photos and upload them.
            </span>
            <span v-if="item.state === 203" class="text-error">
              The file type is incorrect. Please check and re-upload.
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="empty-state-container">
    <h1 class="nores">No test results yet.</h1>
  </div>
</template>

<style scoped>
.results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-surface {
  border: 1px solid var(--td-border-color);
  background: var(--td-panel-bg);
  border-radius: 16px;
  box-shadow: var(--td-soft-shadow);
  overflow: hidden;
}

.result-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--td-border-color);
  background: var(--td-surface);
}

.result-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--td-text-main);
  font-weight: 600;
}

.result-grid {
  display: flex;
  flex-direction: column;
}

.result-item {
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--td-border-color);
}

.result-item:last-child {
  border-bottom: none;
}

.label {
  width: 120px;
  padding: 16px 20px;
  background: var(--td-surface);
  color: var(--td-text-secondary);
  font-weight: 500;
  font-size: 14px;
  border-right: 1px solid var(--td-border-color);
  flex-shrink: 0;
}

.value {
  padding: 16px 20px;
  color: var(--td-text-main);
  font-size: 14px;
  flex: 1;
}

.tag-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  background: var(--td-primary-soft);
  color: var(--td-primary-700);
  text-decoration: none;
  font-size: 12px;
  transition: background 0.2s;
}

.tag-link:hover {
  background: var(--td-primary-100);
}

.text-pending {
  color: var(--td-warning-500);
}

.text-success {
  color: var(--td-success-600);
}

.text-error {
  color: var(--td-danger-500);
}

.empty-state-container {
  padding: 40px;
  display: flex;
  justify-content: center;
}

.nores {
  text-align: center;
  color: var(--td-primary-500);
  font-size: 24px;
  margin: 0;
}

@media (min-width: 768px) {
  .result-grid {
    flex-direction: row;
  }
  .result-item {
    border-bottom: none;
    border-right: 1px solid var(--td-border-color);
  }
  .result-item:last-child {
    border-right: none;
  }
  .img-col {
    width: 35%;
  }
  .text-col {
    flex: 1;
  }
}
</style>