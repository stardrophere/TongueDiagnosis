<script setup>
import { onMounted } from 'vue'
import { useDiagnosisWorkspace } from '@/composables/useDiagnosisWorkspace'
import SessionSidebar from '@/components/diagnosis/SessionSidebar.vue'
import MainContainer from '@/components/mainPage/mainContainer.vue'

const workspace = useDiagnosisWorkspace()

/**
 * 进入诊断页时先尝试加载历史会话。
 * 如果当前账号还没有任何诊断记录，页面会展示空状态，引导用户手动新建。
 */
onMounted(() => {
  workspace.loadSessions()
})
</script>

<template>
  <section class="diagnosis-page page-section">
    <div class="diagnosis-layout">
      <SessionSidebar
        :sessions="workspace.sessions"
        :active-session-id="workspace.activeSessionId"
        :draft-session-name="workspace.draftSessionName"
        :has-draft="workspace.hasDraft"
        :loading="workspace.loadingSessions"
        @create-draft="workspace.createDraft()"
        @select-session="workspace.openSession"
        @update-draft-name="workspace.updateDraftName"
      />

      <MainContainer
        class="workspace-panel"
        :messages="workspace.activeMessages"
        :mode="workspace.workspaceMode"
        :loading="workspace.loadingMessages"
        :can-send="workspace.canSendMessage"
        :can-upload="workspace.canUploadImage"
        :uploading="workspace.uploadingImage"
        :streaming="workspace.streamingReply"
        @request-draft="workspace.createDraft()"
        @submit-image="workspace.submitImage($event.file, $event.previewUrl)"
        @submit-message="workspace.submitMessage"
      />
    </div>
  </section>
</template>

<style scoped>
.diagnosis-page {
  padding: 24px 0 40px;
}

.diagnosis-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.workspace-panel {
  min-width: 0;
}

@media (max-width: 1200px) {
  .diagnosis-layout {
    grid-template-columns: 1fr;
  }
}
</style>
