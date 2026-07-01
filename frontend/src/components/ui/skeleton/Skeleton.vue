<script setup lang="ts">
import { computed } from 'vue'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const delegatedProps = computed(() => ({
  class: cn('animate-pulse rounded-md bg-primary/10', props.class),
}))
</script>

<template>
  <div v-bind="delegatedProps" />
</template>
