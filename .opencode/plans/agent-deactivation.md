# Agent Deactivation with isSupreme Flag

## Overview
Add an `isSupreme` boolean field to the user model. Supreme admins can deactivate other admin agents. When an agent is deactivated, tickets assigned to them (via `[ASSIGNED_TO:...]` in `admin_notes`) are automatically unassigned.

## 1. Database Schema Changes

### `backend/prisma/schema.prisma`
- Add `isSupreme Boolean @default(false)` to the `user` model (after `suspended`)

### `auth-server/prisma/schema.prisma`
- Add `isSupreme Boolean @default(false)` to the `user` model (after `suspended`)

### `auth-server/auth.ts`
- Add `isSupreme` to `additionalFields`:
```ts
isSupreme: {
  type: "boolean",
  required: false,
  defaultValue: false,
  input: true,
},
```

### Migration
- Run `npx prisma migrate dev` in both `backend/` and `auth-server/` to create migration

## 2. Backend Changes

### `backend/app/routes/admin.py`
- Add `get_supreme_admin_user` dependency:
```python
async def get_supreme_admin_user(authorization: Optional[str] = Header(None)):
    # Same as get_admin_user but also checks user.isSupreme == True
    # Raises 403 if not supreme admin
```

### `backend/app/routes/users.py`
- Add `POST /admin/users/{user_id}/deactivate-agent`:
  - Only accessible by supreme admin (`get_supreme_admin_user`)
  - Cannot deactivate yourself
  - Sets `suspended = true`
  - Revokes all sessions
  - Clears `[ASSIGNED_TO:{user_id}|...]` prefix from `adminNotes` on all matching tickets
- Add `POST /admin/users/{user_id}/activate-agent`:
  - Only accessible by supreme admin
  - Sets `suspended = false`
- Remove the `if user.role == "admin": raise HTTPException(400, "Cannot suspend another admin")` restriction from the existing suspend endpoint

### Agent assignment clearing logic (in deactivate-agent endpoint):
```python
import re
tickets = await db.support_tickets.find_many(
    where={"adminNotes": {"contains": f"[ASSIGNED_TO:{user_id}|"}}
)
for ticket in tickets:
    cleaned = re.sub(r'\[ASSIGNED_TO:.*?\|.*?\]\n?\s*', '', ticket.adminNotes or '')
    await db.support_tickets.update(
        where={"id": ticket.id},
        data={"adminNotes": cleaned.strip() or None}
    )
```

## 3. Frontend Changes

### New: `frontend/src/composables/useAdminAgents.ts`
- `useAdminAgents()` — fetches admin users
- `deactivateAgent(userId)` mutation — calls `POST /admin/users/{user_id}/deactivate-agent`
- `activateAgent(userId)` mutation — calls `POST /admin/users/{user_id}/activate-agent`

### New: `frontend/src/components/AgentsTable.vue`
- Table listing all admin users
- Shows name, email, role, status (active/deactivated)
- Deactivate/Activate buttons (visible only when current user `isSupreme === true`)

### Update: `frontend/src/composables/useSupportTickets.ts`
- `useSupportAgents()` — filter out suspended (`suspended === true`) agents from the assignable agent list

### Update: `frontend/src/views/AdminDashboard.vue`
- Add "Agents" tab/section (visible only to supreme admins)
- Render `AgentsTable` component

## 4. Access Control

| User Type | Can suspend clients | Can deactivate agents |
|---|---|---|
| Regular admin (`isSupreme=false`) | Yes | No |
| Supreme admin (`isSupreme=true`) | Yes | Yes |

## 5. Files to Modify
1. `backend/prisma/schema.prisma` — Add `isSupreme` field
2. `auth-server/prisma/schema.prisma` — Add `isSupreme` field
3. `auth-server/auth.ts` — Add `isSupreme` to additionalFields
4. `backend/app/routes/admin.py` — Add `get_supreme_admin_user`
5. `backend/app/routes/users.py` — Add deactivate/activate agent endpoints, remove admin suspend restriction
6. `frontend/src/composables/useSupportTickets.ts` — Filter deactivated agents
7. `frontend/src/views/AdminDashboard.vue` — Add Agents section
8. **New:** `frontend/src/components/AgentsTable.vue`
9. **New:** `frontend/src/composables/useAdminAgents.ts`
