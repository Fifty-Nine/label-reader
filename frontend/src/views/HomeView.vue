<script setup lang="ts">
import { ref } from 'vue'

const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] || null
  } else {
    selectedFile.value = null
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleSubmit = () => {
  if (!selectedFile.value) {
    alert('Please select a file first.')
    return
  }
  // TODO: Implementation for Phase 1 Step 6
  console.log('Submitting file:', selectedFile.value.name)
}
</script>

<template>
  <div class="card">
    <h1 class="title">Inventory Label Reader</h1>

    <form @submit.prevent="handleSubmit" class="upload-form">
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
          <button type="button" class="btn-choose" @click="triggerFileInput">Choose File</button>
          <span class="file-name">
            {{ selectedFile ? selectedFile.name : 'No file chosen' }}
          </span>
        </div>
      </div>

      <button type="submit" class="btn-primary" :disabled="!selectedFile">Process Upload</button>
    </form>
  </div>
</template>

<style scoped>
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
</style>
