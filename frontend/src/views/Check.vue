<script setup>
import { onMounted } from 'vue'
import SessionSidebar from '@/components/diagnosis/SessionSidebar.vue'
import MainContainer from '@/components/mainPage/mainContainer.vue'
import { useDiagnosisWorkspace } from '@/composables/useDiagnosisWorkspace'

const workspace = useDiagnosisWorkspace()
const {
  sessions,
  activeSessionId,
  draftSessionName,
  hasDraft,
  loadingSessions,
  activeMessages,
  workspaceMode,
  loadingMessages,
  canSendMessage,
  canUploadImage,
  uploadingImage,
  streamingReply,
  deletingSessionId,
} = workspace

onMounted(() => {
  workspace.loadSessions()
})
</script>

<template>
  <section class="diagnosis-page page-section">
    <div class="diagnosis-layout">
      <SessionSidebar
        :sessions="sessions"
        :active-session-id="activeSessionId"
        :draft-session-name="draftSessionName"
        :has-draft="hasDraft"
        :loading="loadingSessions"
        :deleting-session-id="deletingSessionId"
        @create-draft="workspace.createDraft()"
        @select-session="workspace.openSession"
        @update-draft-name="workspace.updateDraftName"
        @delete-session="workspace.deleteSession"
      />

      <MainContainer
        class="workspace-panel"
        :messages="activeMessages"
        :mode="workspaceMode"
        :loading="loadingMessages"
        :can-send="canSendMessage"
        :can-upload="canUploadImage"
        :uploading="uploadingImage"
        :streaming="streamingReply"
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
  height: calc(100vh - 112px);
}

.diagnosis-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 20px;
  align-items: stretch;
  height: 100%;
  min-height: 0;
}

.workspace-panel {
  min-width: 0;
  min-height: 0;
  height: 100%;
}

@media (max-width: 900px) {
  .diagnosis-page {
    height: auto;
  }

  .diagnosis-layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .workspace-panel {
    height: auto;
  }
}
</style>
