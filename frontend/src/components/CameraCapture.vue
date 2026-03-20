<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits<{
  (e: 'capture', file: File, url: string): void
  (e: 'clear'): void
  (e: 'error', message: string): void
}>()

const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const cameraStream = ref<MediaStream | null>(null)
const capturedImageUrl = ref<string | null>(null)

const startCamera = async () => {
  try {
    if (!window.isSecureContext) {
      throw new Error('Camera access requires a secure context (HTTPS or localhost).')
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported in this browser context.')
    }
    cameraStream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
    })
    if (videoElement.value) {
      videoElement.value.srcObject = cameraStream.value
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
    emit(
      'error',
      error instanceof Error ? error.message : 'Failed to access camera. Please check permissions.',
    )
  }
}

const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((track) => track.stop())
    cameraStream.value = null
  }
}

onMounted(() => {
  startCamera()
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
        if (capturedImageUrl.value) {
          URL.revokeObjectURL(capturedImageUrl.value)
        }
        capturedImageUrl.value = URL.createObjectURL(blob)
        stopCamera()
        emit('capture', file, capturedImageUrl.value)
      }
    }, 'image/jpeg')
  }
}

const clearCapture = () => {
  if (capturedImageUrl.value) {
    URL.revokeObjectURL(capturedImageUrl.value)
    capturedImageUrl.value = null
  }
  emit('clear')
  startCamera()
}
</script>

<template>
  <div class="camera-container" v-if="!capturedImageUrl">
    <video ref="videoElement" autoplay playsinline class="camera-video"></video>
    <button type="button" class="btn-secondary" @click="captureImage">Capture</button>
  </div>
  <div class="capture-preview" v-else>
    <img :src="capturedImageUrl" alt="Captured Label" class="preview-image" />
    <button type="button" class="btn-secondary" @click="clearCapture">Retake</button>
  </div>
  <canvas ref="canvasElement" style="display: none"></canvas>
</template>

<style scoped>
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
</style>
