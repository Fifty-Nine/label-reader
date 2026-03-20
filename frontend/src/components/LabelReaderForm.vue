<script setup lang="ts">
import { ref, onMounted } from 'vue'
import CameraCapture from './CameraCapture.vue'
import type { ExtractedLabel } from './ResultsTable.vue'

const emit = defineEmits<{
  (e: 'result', data: ExtractedLabel[] | null): void
}>()

const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const capturedImageUrl = ref<string | null>(null)

const models = ref<string[]>([])
const selectedModel = ref<string | null>(null)
const isLoadingModels = ref(false)

const labelDescription = ref<string>('')
const includeDate = ref<boolean>(false)

const activeTab = ref<'upload' | 'camera'>('upload')

onMounted(async () => {
  isLoadingModels.value = true
  try {
    const response = await fetch('/api/models')
    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`)
    }
    const data = await response.json()
    models.value = data.models || []
    if (models.value.length > 0) {
      selectedModel.value = data.default || models.value[0] || null
    }
  } catch (error) {
    console.error('Error fetching models:', error)
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load AI models.'
  } finally {
    isLoadingModels.value = false
  }
})

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] || null
    errorMessage.value = null
    if (capturedImageUrl.value) {
      URL.revokeObjectURL(capturedImageUrl.value)
      capturedImageUrl.value = null
    }
  } else {
    selectedFile.value = null
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleCameraCapture = (file: File, url: string) => {
  selectedFile.value = file
  capturedImageUrl.value = url
  errorMessage.value = null
}

const handleCameraClear = () => {
  selectedFile.value = null
  capturedImageUrl.value = null
}

const handleCameraError = (msg: string) => {
  errorMessage.value = msg
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    errorMessage.value = 'Please select or capture an image first.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = null
  emit('result', null)

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    if (selectedModel.value) {
      formData.append('model_name', selectedModel.value)
    }
    if (labelDescription.value) {
      formData.append('label_desc', labelDescription.value)
    }
    formData.append('include_date', includeDate.value ? 'true' : 'false')

    const response = await fetch('/api/extract', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.detail && Array.isArray(errorData.detail)) {
        throw new Error(errorData.detail.map((e: { msg: string }) => e.msg).join(', '))
      }
      throw new Error(errorData.detail || `Request failed with status ${response.status}`)
    }

    const data = await response.json()
    emit('result', data)
  } catch (error) {
    console.error('Error submitting file:', error)
    errorMessage.value = error instanceof Error ? error.message : 'An unexpected error occurred.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="upload-form">
    <div class="form-group">
      <label>Select AI Model</label>
      <div class="select-wrapper">
        <select
          v-model="selectedModel"
          :disabled="isLoadingModels || models.length === 0"
          class="form-select"
        >
          <option v-if="isLoadingModels" value="" disabled>Loading models...</option>
          <option v-else-if="models.length === 0" value="" disabled>No models available</option>
          <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
        </select>
      </div>
    </div>

    <div class="tabs">
      <button
        type="button"
        @click="activeTab = 'upload'"
        :class="['tab-btn', { active: activeTab === 'upload' }]"
      >
        File Upload
      </button>
      <button
        type="button"
        @click="activeTab = 'camera'"
        :class="['tab-btn', { active: activeTab === 'camera' }]"
      >
        Camera
      </button>
    </div>

    <div v-show="activeTab === 'upload'" class="form-group">
      <label>Select Label Image (JPG)</label>
      <div class="file-input-wrapper">
        <input
          type="file"
          accept="image/*"
          @change="handleFileChange"
          ref="fileInput"
          class="hidden-input"
        />
        <button type="button" class="btn-choose" @click="triggerFileInput" :disabled="isSubmitting">
          Choose File
        </button>
        <span class="file-name">
          {{ selectedFile && !capturedImageUrl ? selectedFile.name : 'No file chosen' }}
        </span>
      </div>
    </div>

    <div v-show="activeTab === 'camera'" class="form-group camera-group">
      <label>Capture Label Image</label>
      <CameraCapture
        v-if="activeTab === 'camera'"
        @capture="handleCameraCapture"
        @clear="handleCameraClear"
        @error="handleCameraError"
      />
    </div>

    <div class="form-group">
      <label for="labelDesc">Label Description (Optional)</label>
      <input
        type="text"
        id="labelDesc"
        v-model="labelDescription"
        placeholder="e.g., Shipping label, product barcode"
        class="form-input"
        :disabled="isSubmitting"
      />
    </div>

    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input type="checkbox" v-model="includeDate" :disabled="isSubmitting" />
        Extract Dates
      </label>
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <button type="submit" class="btn-primary" :disabled="!selectedFile || isSubmitting">
      {{ isSubmitting ? 'Processing...' : 'Process Upload' }}
    </button>
  </form>
</template>

<style scoped>
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--color-text);
  font-weight: 500;
}

.select-wrapper {
  display: flex;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-background-soft);
}

.form-select {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text);
  font-size: 0.9rem;
  cursor: pointer;
  appearance: auto;
  outline: none;
}

.form-select option {
  background-color: var(--color-background);
  color: var(--color-text);
}

.form-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.camera-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
}

.hidden-input {
  display: none;
}

.btn-choose {
  background: var(--color-background-soft);
  border: none;
  border-right: 1px solid var(--color-border);
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--color-text);
}

.file-name {
  padding: 0.75rem 1rem;
  color: var(--color-text-light-2);
  font-size: 0.9rem;
  flex: 1;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background-soft);
  color: var(--color-text);
  font-size: 0.9rem;
  outline: none;
}

.form-input:focus {
  border-color: #0d6efd;
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  margin-bottom: 0 !important;
  font-weight: normal !important;
}

.checkbox-label input[type='checkbox'] {
  cursor: pointer;
}

.btn-primary {
  background: #0d6efd;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  width: 100%;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #0b5ed7;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
