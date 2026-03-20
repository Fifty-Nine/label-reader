<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'

const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

interface ExtractedLabel {
  visual_evidence?: string
  item: string
  date?: string
}

const rawResult = ref<ExtractedLabel[] | null>(null)

const models = ref<string[]>([])
const selectedModel = ref<string | null>(null)
const isLoadingModels = ref(false)

const labelDescription = ref<string>('')
const includeDate = ref<boolean>(false)

const activeTab = ref<'upload' | 'camera'>('upload')
const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const cameraStream = ref<MediaStream | null>(null)
const capturedImageUrl = ref<string | null>(null)

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
  } finally {
    isLoadingModels.value = false
  }
})

const startCamera = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported in this browser context.')
    }
    cameraStream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
    })
    if (videoElement.value) {
      videoElement.value.srcObject = cameraStream.value
    }
    errorMessage.value = null
  } catch (error) {
    console.error('Error accessing camera:', error)
    errorMessage.value =
      error instanceof Error ? error.message : 'Failed to access camera. Please check permissions.'
  }
}

const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((track) => track.stop())
    cameraStream.value = null
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'camera' && !capturedImageUrl.value) {
    startCamera()
  } else {
    stopCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
  if (capturedImageUrl.value) {
    URL.revokeObjectURL(capturedImageUrl.value)
  }
})

const captureImage = () => {
  if (!videoElement.value || !canvasElement.value) return

  const video = videoElement.value
  const canvas = canvasElement.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const context = canvas.getContext('2d')
  if (context) {
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
        selectedFile.value = file
        if (capturedImageUrl.value) {
          URL.revokeObjectURL(capturedImageUrl.value)
        }
        capturedImageUrl.value = URL.createObjectURL(blob)
        stopCamera()
        errorMessage.value = null
      }
    }, 'image/jpeg')
  }
}

const clearCapture = () => {
  selectedFile.value = null
  if (capturedImageUrl.value) {
    URL.revokeObjectURL(capturedImageUrl.value)
    capturedImageUrl.value = null
  }
  startCamera()
}

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

const handleSubmit = async () => {
  if (!selectedFile.value) {
    errorMessage.value = 'Please select or capture an image first.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = null
  rawResult.value = null

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
    console.log('Extraction Result:', data)
    rawResult.value = data
  } catch (error) {
    console.error('Error submitting file:', error)
    errorMessage.value = error instanceof Error ? error.message : 'An unexpected error occurred.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="card">
    <h1 class="title">Inventory Label Reader</h1>

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
          <button
            type="button"
            class="btn-choose"
            @click="triggerFileInput"
            :disabled="isSubmitting"
          >
            Choose File
          </button>
          <span class="file-name">
            {{ selectedFile && !capturedImageUrl ? selectedFile.name : 'No file chosen' }}
          </span>
        </div>
      </div>

      <div v-show="activeTab === 'camera'" class="form-group camera-group">
        <label>Capture Label Image</label>
        <div class="camera-container" v-if="!capturedImageUrl">
          <video ref="videoElement" autoplay playsinline class="camera-video"></video>
          <button type="button" class="btn-secondary" @click="captureImage">Capture</button>
        </div>
        <div class="capture-preview" v-else>
          <img :src="capturedImageUrl" alt="Captured Label" class="preview-image" />
          <button type="button" class="btn-secondary" @click="clearCapture">Retake</button>
        </div>
        <canvas ref="canvasElement" style="display: none"></canvas>
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

    <div v-if="rawResult" class="result-container">
      <h3>Extraction Result</h3>
      <div class="table-responsive">
        <table v-if="rawResult.length > 0" class="result-table">
          <thead>
            <tr>
              <th>Item</th>
              <th v-if="rawResult.some((r) => r.date)">Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in rawResult" :key="index">
              <td>{{ row.item }}</td>
              <td v-if="rawResult.some((r) => r.date)">{{ row.date || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-results">No labels extracted.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.result-container {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.result-container h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: var(--color-heading);
}

.table-responsive {
  overflow-x: auto;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: var(--color-background-soft);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.result-table th,
.result-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.result-table th {
  background-color: var(--color-background-mute);
  font-weight: 600;
  color: var(--color-heading);
}

.result-table tr:last-child td {
  border-bottom: none;
}

.no-results {
  color: var(--color-text-light-2);
  font-style: italic;
  font-size: 0.9rem;
}

.card {
  background: var(--color-background);
  border-radius: 12px;
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  margin-top: 2rem;
}

.title {
  text-align: center;
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 2rem;
  color: var(--color-heading);
}

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

.camera-container,
.capture-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 1rem;
  background: var(--color-background-soft);
}

.camera-video,
.preview-image {
  width: 100%;
  max-width: 100%;
  border-radius: 6px;
  background: #000;
}

.preview-image {
  background: transparent;
  border: 1px solid var(--color-border);
}

.btn-secondary {
  background: var(--color-background-mute);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: var(--color-border);
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
