<script lang="ts" setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { LoaderCircle, Mail, Phone, Shield } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

watch([user, loading], ([u, l]) => {
  if (!l && !u) {
    router.replace('/login')
  }
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8">
    <div v-if="loading" class="text-center">
      <LoaderCircle class="size-8 text-primary animate-spin mx-auto mb-4" />
      <p class="text-muted-foreground">Loading...</p>
    </div>

    <div v-else-if="user" class="text-center max-w-lg">
      <Avatar size="lg" class="mx-auto mb-6">
        <AvatarFallback>{{ user.name?.charAt(0)?.toUpperCase() }}</AvatarFallback>
      </Avatar>

      <h1 class="text-3xl font-bold text-foreground mb-2">
        Welcome back, {{ user.name }}!
      </h1>
      <p class="text-muted-foreground mb-8">
        You are signed in as
        <Badge variant="secondary" class="ml-1 capitalize">{{ user.role }}</Badge>
      </p>

      <Separator class="mb-8" />

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent class="flex flex-col items-center gap-3 pt-6">
            <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <Shield class="size-5 text-primary" />
            </div>
            <div class="text-center">
              <p class="text-sm text-muted-foreground">Role</p>
              <p class="text-lg font-bold text-foreground capitalize">{{ user.role }}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="flex flex-col items-center gap-3 pt-6">
            <div class="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
              <Mail class="size-5 text-green-600" />
            </div>
            <div class="text-center">
              <p class="text-sm text-muted-foreground">Email</p>
              <p class="text-sm font-bold text-foreground truncate">{{ user.email }}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="flex flex-col items-center gap-3 pt-6">
            <div class="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <Phone class="size-5 text-purple-600" />
            </div>
            <div class="text-center">
              <p class="text-sm text-muted-foreground">Phone</p>
              <p class="text-sm font-bold text-foreground">{{ user.phone || 'Not set' }}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
