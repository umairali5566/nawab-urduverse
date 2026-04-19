#!/bin/bash
# RENDER DEPLOYMENT COMMANDS
# Copy-paste these commands in order

# ============================================
# STEP 1: VERIFY LOCAL STATE (Already done)
# ============================================
# ✓ Admin loads: python manage.py runserver
# ✓ No errors visible
# ✓ Migrations applied

# ============================================
# STEP 2: GIT COMMIT & PUSH
# ============================================

# Check status
git status

# Add migration if needed
git add blog/migrations/0002_blogpost_featured_image.py

# Commit changes
git commit -m "Fix: Add featured_image to BlogPost + Production safety commands

- Added featured_image field to BlogPost model (null=True, blank=True)
- Created safety management commands to prevent makemigrations on Render
- migrate command runs non-interactive on Render
- makemigrations blocked on Render with clear error message
- All migrations generated and tested locally
- Admin interface verified working
- Media and CKEditor settings verified correct"

# Push to Render (this triggers deployment)
git push origin main

# ============================================
# STEP 3: MONITOR DEPLOYMENT
# ============================================
# Go to: https://dashboard.render.com
# Click: nawab-urdu-academy
# Watch: "Build & Deploys" tab
#
# You should see:
# ✓ Building...
# ✓ pip install -r requirements.txt
# ✓ python manage.py migrate
# ✓   Applying blog.0002_blogpost_featured_image... OK
# ✓ python manage.py collectstatic --noinput
# ✓ Build succeeded

# Wait for status to show "Live" (green)
# Takes 2-5 minutes

# ============================================
# STEP 4: VERIFY PRODUCTION
# ============================================

# 1. Open admin
#    URL: https://your-domain.com/admin/
#    Login with your credentials

# 2. Click each model:
#    - Should NOT see 500 errors
#    - Data should load normally
#    - Models: Categories, Authors, Quotes, Poetry, Stories, etc.

# 3. Try creating an item:
#    - Blog Posts → Add Blog Post
#    - Leave image empty
#    - Click Save
#    - Should save without errors

# 4. Check Render logs:
#    - Dashboard → Logs
#    - Look for: "Applying blog.0002_blogpost_featured_image... OK"
#    - Should NOT see: "500", "EOFError", "nullable field"

# ============================================
# STEP 5: CONFIRM SUCCESS
# ============================================

# If you see:
# ✅ Admin loads
# ✅ No 500 errors
# ✅ Models clickable
# ✅ Migration applied in logs
# ✅ Can create items with/without images

# THEN: Deployment was SUCCESSFUL! 🎉

# ============================================
# STEP 6: EMERGENCY ROLLBACK (If needed)
# ============================================

# If something goes wrong:

git log --oneline | head -5
# Find the commit before your push

git revert <commit-hash>
git push origin main

# Wait for Render to redeploy with previous version
# Takes 2-5 minutes

# ============================================
# COMMANDS SUMMARY
# ============================================

# For reference - what Render runs automatically:
# 1. pip install -r requirements.txt
# 2. python manage.py migrate --no-input
# 3. python manage.py collectstatic --noinput

# What is BLOCKED (by safety commands):
# ❌ python manage.py makemigrations (blocked on Render)
#    → Raises: CommandError with clear message
#    → You'll see instructions to generate locally

# ============================================
# CLEANUP (Local only - don't push)
# ============================================

# If you want to clean up local database for fresh test:
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Then test admin locally before pushing

# ============================================
# FINAL CHECKLIST
# ============================================

# Before pushing:
# ☐ All migrations committed: git status (clean)
# ☐ Blog migrations in git: ls blog/migrations/
# ☐ Admin works locally: python manage.py runserver
# ☐ No errors on model click
# ☐ Featured image not required on forms

# After pushing:
# ☐ Render shows "Live" (green)
# ☐ Admin loads: https://your-domain.com/admin/
# ☐ Models clickable without 500 errors
# ☐ Logs show migration: "Applying blog.0002_blogpost_featured_image... OK"
# ☐ Can create items with/without images

# ============================================
# REFERENCE: What Changed
# ============================================

# Files Created:
# - accounts/management/commands/makemigrations.py (blocks on Render)
# - accounts/management/commands/migrate.py (non-interactive on Render)
# - blog/migrations/0002_blogpost_featured_image.py (new field)

# Files Modified:
# - blog/models.py (added featured_image field)
# - blog/admin.py (added featured_image to fieldsets)

# Files Already Correct (no changes):
# - nawab_urduverse/settings.py (MEDIA settings OK)
# - render.yaml (build command OK)
# - All models have null=True, blank=True

# ============================================
# SUCCESS INDICATORS
# ============================================

# ✅ Deployment successful if:
# 1. Build completed on Render (no errors)
# 2. Admin page loads at /admin/
# 3. Can click all models
# 4. No 500 errors
# 5. Migration shows in logs
# 6. Can save items with/without images

# ❌ Rollback needed if:
# 1. Build failed on Render
# 2. Admin shows 500 errors
# 3. Models won't load
# 4. Migration error in logs

# → Run: git revert <hash> && git push origin main

# ============================================
# SUPPORT & TROUBLESHOOTING
# ============================================

# See: PRODUCTION_FIX_COMPLETE.md (full details)
# See: DEPLOYMENT_CHECKLIST.md (step-by-step)
# See: RENDER_FIX_SUMMARY.md (technical details)

echo "✅ All commands ready for deployment"
echo "📋 Next: Review this file, then git push origin main"
echo "📊 Monitor: https://dashboard.render.com"
