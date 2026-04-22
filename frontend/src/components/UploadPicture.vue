<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadMaxSizeMb } from '@/config/appConfig'

const emit = defineEmits(['selected'])

/**
 * 校验并预览选中的图片文件
 */
function handleFileChange(uploadFile) {
  const file = uploadFile.raw

  if (!file) {
    return false
  }

  const allowTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp']
  if (!allowTypes.includes(file.type)) {
    ElMessage.warning('请上传 JPG、PNG、BMP 或 WEBP 格式的图片。')
    return false
  }

  if (file.size / 1024 / 1024 > uploadMaxSizeMb) {
    ElMessage.warning(`图片大小不能超过 ${uploadMaxSizeMb}MB。`)
    return false
  }

  const reader = new FileReader()
  reader.onload = (event) => {
    emit('selected', {
      file,
      previewUrl: event.target?.result || '',
      name: file.name,
    })
  }
  reader.readAsDataURL(file)

  return false
}
</script>

<template>
  <el-upload
    class="upload-demo"
    drag
    :auto-upload="false"
    :show-file-list="false"
    accept=".jpg,.jpeg,.png,.bmp,.webp"
    :on-change="handleFileChange"
  >
    <el-icon class="el-icon--upload">
      <UploadFilled />
    </el-icon>
    <div class="el-upload__text">
      <strong>拖拽图片到这里</strong>
      <p>或点击选择舌象图片，支持 JPG / PNG / BMP / WEBP</p>
    </div>
  </el-upload>
</template>

<style scoped>
.upload-demo {
  width: 100%;
  min-height: 188px;
}

::deep(.el-upload),
::deep(.el-upload-dragger) {
  width: 100%;
}

::deep(.el-upload-dragger) {
  display: flex;
  min-height: 188px;
  border: 1px dashed var(--td-border-strong);
  border-radius: 24px;
  background: var(--td-panel-strong);
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--td-text-main);
}

::deep(.el-icon--upload) {
  margin-bottom: 16px;
  font-size: 54px;
  color: var(--td-primary-600);
}

::deep(.el-upload__text strong) {
  display: block;
  margin-bottom: 6px;
}

::deep(.el-upload__text p) {
  margin: 0;
  color: var(--td-text-muted);
}
</style>
