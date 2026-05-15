# TODO_ADMIN.md

## Moderation endpoints connection (admin review)
- [x] 1. Create moderation schema fields for notes/tasks/files (`moderation_status`).

- [x] 2. Add admin moderation backend routes & controllers:
  - [ ] a. List pending notes/tasks/files
  - [ ] b. Approve note/task/file
  - [ ] c. Reject note/task/file
- [x] 3. Wire blueprint into `backend/app.py` under `/api/auth`.
- [x] 4. Update create flows:

  - [x] a. Notes creation sets `moderation_status='pending'`

  - [x] b. Tasks creation sets `moderation_status='pending'`

  - [x] c. File upload sets `moderation_status='pending'`

- [x] 5. Enforce visibility:

  - [x] a. Owners can view pending items

  - [x] b. Non-owners only see approved items (and shared rules follow the same constraint)

- [ ] 6. Implement frontend moderation UIs:
  - [ ] a. `review-notes.html` list pending + approve/reject
  - [ ] b. `review-tasks.html` list pending + approve/reject
  - [ ] c. `review-files.html` list pending + approve/reject
- [ ] 7. Manual verification:
  - [ ] a. Login as admin
  - [ ] b. Create user content and verify it lands in pending queue
  - [ ] c. Approve/reject from admin UI and verify effect

