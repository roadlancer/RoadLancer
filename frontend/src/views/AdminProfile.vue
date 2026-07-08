<script lang="ts" setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'
import { Shield } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'admin') router.replace('/')
  }
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8">
    <div v-if="loading" class="text-center max-w-lg w-full">
      <Skeleton class="h-9 w-48 mx-auto mb-2" />
      <Skeleton class="h-5 w-64 mx-auto mb-6" />
      <Card>
        <CardHeader>
          <Skeleton class="h-6 w-32 mb-2" />
          <Skeleton class="h-4 w-48" />
        </CardHeader>
        <CardContent class="space-y-3">
          <Skeleton class="h-4 w-full" />
          <Skeleton class="h-4 w-full" />
          <Skeleton class="h-4 w-2/3" />
        </CardContent>
      </Card>
    </div>
    <div v-else-if="user?.role === 'admin'" class="text-center max-w-lg w-full">
      <h1 class="text-3xl font-bold text-foreground mb-2">Admin Profile</h1>
      <p class="text-muted-foreground mb-6">Your administrator account details</p>

      <Card class="bg-card text-card-foreground border border-border shadow-sm">
        <CardHeader class="border-b border-border pb-6">
          <div class="flex items-center gap-4">
            <Avatar class="size-16 border border-border">
              <AvatarFallback class="text-xl bg-primary/10 text-primary font-semibold">
                {{ user.name?.charAt(0)?.toUpperCase() }}
              </AvatarFallback>
            </Avatar>
            <div class="text-left">
              <CardTitle class="flex items-center gap-2 text-2xl font-bold text-foreground">
                <Shield class="size-5 text-primary" />
                {{ user.name }}
              </CardTitle>
              <CardDescription class="text-muted-foreground">
                Administrator
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent class="space-y-4 pt-6 text-left">
          <div class="flex items-center justify-between py-1 border-b border-border/50">
            <span class="text-muted-foreground text-sm font-medium">Name</span>
            <span class="text-sm font-semibold text-foreground">{{ user.name }}</span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-border/50">
            <span class="text-muted-foreground text-sm font-medium">Email</span>
            <span class="text-sm font-semibold text-foreground">{{ user.email }}</span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-border/50">
            <span class="text-muted-foreground text-sm font-medium">Phone</span>
            <span class="text-sm font-semibold text-foreground">{{ user.phone || 'Not set' }}</span>
          </div>
          <div class="flex items-center justify-between py-1">
            <span class="text-muted-foreground text-sm font-medium">Role</span>
            <span class="text-sm font-semibold text-primary capitalize">{{ user.role }}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
