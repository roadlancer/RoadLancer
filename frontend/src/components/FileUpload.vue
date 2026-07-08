<script lang="ts" setup>
import { ref, computed } from 'vue'
import { UploadCloud, X, FileCheck, AlertCircle } from '@lucide/vue'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  modelValue?: string | null
  label?: string
  accept?: string
  maxSizeMb?: number
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const error = ref<string | null>(null)
const isDragging = ref(false)

const acceptedTypes = computed(() => props.accept || 'image/jpeg,image/png,image/webp')
const maxLimit = computed(() => (props.maxSizeMb || 5) * 1024 * 1024)

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    processFile(files[0])
  }
}

function handleDrop(event: DragEvent) {
  if (props.disabled) return
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    processFile(files[0])
  }
}

function processFile(file: File) {
  error.value = null

  // Validate type
  if (!file.type.startsWith('image/')) {
    error.value = 'Only image files (JPEG, PNG, WebP) are allowed.'
    return
  }

  // Validate size
  if (file.size > maxLimit.value) {
    error.value = `File size exceeds maximum limit of ${props.maxSizeMb || 5}MB.`
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    emit('update:modelValue', result)
  }
  reader.onerror = () => {
    error.value = 'Failed to read file.'
  }
  reader.readAsDataURL(file)
}

function triggerSelect() {
  if (!props.disabled) {
    fileInputRef.value?.click()
  }
}

function clearFile() {
  if (props.disabled) return
  emit('update:modelValue', null)
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}
</script>

<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium text-foreground">
      {{ label }}
    </label>

    <div
      v-if="!modelValue"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerSelect"
      class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors flex flex-col items-center justify-center gap-2 select-none"
      :class="[
        disabled ? 'opacity-50 cursor-not-allowed bg-muted/50 border-border' : isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-accent/50'
      ]"
    >
      <input
        ref="fileInputRef"
        type="file"
        :accept="acceptedTypes"
        class="hidden"
        :disabled="disabled"
        @change="handleFileChange"
      />
      <div class="rounded-full bg-primary/10 p-3 text-primary">
        <UploadCloud class="size-6" />
      </div>
      <div class="text-sm">
        <span class="font-semibold text-primary">Click to upload</span> or drag and drop
      </div>
      <p class="text-xs text-muted-foreground">
        PNG, JPG or WebP (max {{ maxSizeMb || 5 }}MB)
      </p>
    </div>

    <div
      v-else
      class="relative border rounded-lg p-3 flex items-center gap-3 bg-card text-card-foreground shadow-xs"
    >
      <div class="size-14 rounded-md overflow-hidden bg-muted flex-shrink-0 border flex items-center justify-center">
        <img :src="modelValue" alt="Uploaded document" class="w-full h-full object-cover" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-foreground flex items-center gap-1.5 truncate">
          <FileCheck class="size-4 text-green-600 flex-shrink-0" />
          Document Attached
        </p>
        <p class="text-xs text-muted-foreground truncate">
          Ready for submission
        </p>
      </div>
      <Button
        v-if="!disabled"
        variant="ghost"
        size="icon"
        class="size-8 text-muted-foreground hover:text-destructive"
        @click.stop="clearFile"
        title="Remove document"
      >
        <X class="size-4" />
      </Button>
    </div>

    <p v-if="error" class="text-xs text-destructive flex items-center gap-1">
      <AlertCircle class="size-3.5 flex-shrink-0" />
      {{ error }}
    </p>
  </div>
</template>
