<script setup lang="ts">
import { ref, onMounted } from 'vue'

const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const rawResult = ref<unknown>(null)

const models = ref<string[]>([])
const selectedModel = ref<string | null>(null)
const isLoadingModels = ref(false)

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
      selectedModel.value = models.value[0] || null
    }
  } catch (error) {
    console.error('Error fetching models:', error)
  } finally {
    isLoadingModels.value = false
  }
})

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] || null
    errorMessage.value = null
  } else {
    selectedFile.value = null
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    errorMessage.value = 'Please select a file first.'
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

    const response = await fetch('/api/extract', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
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

      <div class="form-group">
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
            {{ selectedFile ? selectedFile.name : 'No file chosen' }}
          </span>
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>

      <button type="submit" class="btn-primary" :disabled="!selectedFile || isSubmitting">
        {{ isSubmitting ? 'Processing...' : 'Process Upload' }}
      </button>
    </form>

    <div v-if="rawResult" class="result-container">
      <h3>Extraction Result</h3>
      <pre>{{ JSON.stringify(rawResult, null, 2) }}</pre>
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

pre {
  background: var(--color-background-soft);
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
  border: 1px solid var(--color-border);
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
