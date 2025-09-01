# 🚨 CRITICAL: CI/CD Workflow Directory

## ⚠️ IMPORTANT RULES

### ✅ DO:
- Only modify `production.yml` if absolutely necessary
- Test any changes locally first
- Keep job names simple and unique

### ❌ DON'T:
- Create multiple workflow files
- Use conflicting job names (`test`, `security-scan`, etc.)
- Add backup/old workflow files to git

## 📋 Current Active Workflow

**File**: `production.yml`  
**Jobs**: 
- `code-quality` - Validates project structure and syntax
- `security` - Basic security checks (continue-on-error)
- `deploy` - Deployment notification

## 🛠️ If You Need to Modify the Workflow:

1. **Backup approach**: Copy the working content locally, don't commit backup files
2. **Test changes**: Make small incremental changes
3. **Use unique job names**: Avoid common names that might conflict
4. **One workflow only**: Never have multiple .yml files in this directory

## 📊 Current Status: ✅ WORKING PERFECTLY

This workflow successfully:
- ✅ Validates code quality
- ✅ Runs security checks  
- ✅ Triggers deployment notifications
- ✅ No conflicts or failures

**DO NOT MODIFY UNLESS ABSOLUTELY NECESSARY**
