# Recipe System Sequence Fix Guide

## Problem Description
PostgreSQL sequences for Recipe-related tables can become out of sync, causing UniqueViolation/IntegrityError errors:

### Recipe Table Error:
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "recipe_recipe_pkey"
DETAIL: Key (id)=(12) already exists.
```

### RecipeIngredient Table Error:
```
django.db.utils.IntegrityError: duplicate key value violates unique constraint "recipe_recipeingredient_pkey"
DETAIL: Key (id)=(4) already exists.
```

## Solution: Enhanced Django Management Command

### Command Location
```
backend/cocktails/apps/recipe/management/commands/fix_recipe_sequence.py
```

### Usage

#### 1. Check All Tables (Recommended First Step)
```bash
cd backend/cocktails
source ../.venv/bin/activate
python manage.py fix_recipe_sequence --dry-run --verbose
```

#### 2. Fix All Tables
```bash
python manage.py fix_recipe_sequence --verbose
```

#### 3. Fix Specific Tables
```bash
# Fix only Recipe table
python manage.py fix_recipe_sequence --table recipe --verbose

# Fix only RecipeIngredient table  
python manage.py fix_recipe_sequence --table ingredient --verbose
```

### Command Features

#### 🔍 Multi-Table Diagnostic Phase
- Checks both `recipe_recipe` and `recipe_recipeingredient` tables
- Analyzes max ID vs sequence values for each table
- Detects conflicts independently per table
- Provides detailed status for each table

#### 🛠️ Selective Fix Phase  
- Can fix all tables or specific tables
- Synchronizes sequences with `max(id) + 1`
- Verifies fixes were applied correctly
- Tests that next IDs will be conflict-free

#### 🧪 Enhanced Testing Phase
- Simulates next ID generation for each table
- Confirms no conflicts will occur
- Provides comprehensive reporting

### Example Output

#### All Tables Processing:
```
🔧 PostgreSQL Recipe System Sequence Fix Utility
📋 Processing 2 table(s): all

🍸 Recipe Table Processing
🔍 Step 1: Diagnosing Recipe state...
📊 Records in recipe_recipe: 1174
📈 Maximum ID in table: 1174
📊 Last sequence value: 1177
✅ No sequence conflict detected
✅ Step 2: No Recipe sequence fix needed

🥃 RecipeIngredient Table Processing  
🔍 Step 1: Diagnosing RecipeIngredient state...
📊 Records in recipe_recipeingredient: 1250
📈 Maximum ID in table: 1255
🔢 Current sequence value: 4
⚠️ SEQUENCE CONFLICT DETECTED!
   Sequence value (4) <= Max ID (1255)
🛠️ Step 2: Fixing RecipeIngredient sequence...
🎯 Setting sequence to: 1256
✅ Sequence updated successfully to: 1256

📋 FINAL SUMMARY REPORT
==================================================
🍸 Recipe: ✅ OK
🥃 RecipeIngredient: ⚠️ CONFLICT DETECTED

🎉 RECIPE SYSTEM SEQUENCE FIX COMPLETED
📝 Summary of changes:
   - RecipeIngredient sequence synchronized
   - UniqueViolation/IntegrityError errors should be resolved
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Show what would be done without making changes | `--dry-run` |
| `--verbose` | Show detailed output and testing | `--verbose` |
| `--table` | Specify which table: `recipe`, `ingredient`, `all` | `--table ingredient` |

### When to Use

#### Run this command when:
- Getting UniqueViolation errors on Recipe creation
- Getting IntegrityError errors on RecipeIngredient creation
- After importing Recipe/Ingredient data from external sources
- After manual database modifications
- As part of deployment process (preventive)

#### Emergency Usage:
If Recipe creation is completely broken:
```bash
# Quick fix for all tables
python manage.py fix_recipe_sequence

# Quick fix for specific problem
python manage.py fix_recipe_sequence --table ingredient
```

### Technical Details

#### SQL Commands Used:
```sql
-- Check current sequences
SELECT currval(pg_get_serial_sequence('recipe_recipe', 'id'));
SELECT currval(pg_get_serial_sequence('recipe_recipeingredient', 'id'));

-- Find max IDs
SELECT MAX(id) FROM recipe_recipe;
SELECT MAX(id) FROM recipe_recipeingredient;

-- Fix sequences
SELECT setval(pg_get_serial_sequence('recipe_recipe', 'id'), <new_value>);
SELECT setval(pg_get_serial_sequence('recipe_recipeingredient', 'id'), <new_value>);
```

#### Processed Tables:
1. **recipe_recipe** (🍸 Recipe) - Main cocktail records
2. **recipe_recipeingredient** (🥃 RecipeIngredient) - Cocktail ingredients

#### Safety Features:
- Dry-run mode for safe testing
- Per-table processing and reporting  
- Selective table fixing
- Detailed logging with status indicators
- Error handling with rollback
- Verification of fixes applied

### Integration with Deployment

Add to deployment scripts:
```bash
# In deployment script - check first
python manage.py fix_recipe_sequence --dry-run

# Apply fixes if needed
python manage.py fix_recipe_sequence

# Or be more specific
python manage.py fix_recipe_sequence --table all --verbose
```

### Troubleshooting

#### Common Scenarios:

1. **Recipe OK, RecipeIngredient has conflict**:
   ```bash
   python manage.py fix_recipe_sequence --table ingredient
   ```

2. **Both tables have conflicts**:
   ```bash
   python manage.py fix_recipe_sequence --table all
   ```

3. **Only Recipe has conflict** (rare):
   ```bash
   python manage.py fix_recipe_sequence --table recipe
   ```

### Maintenance

This command can be run safely multiple times:
- If no conflicts exist, it reports "OK" and exits
- If conflicts exist, it fixes and reports changes
- Always safe to run as preventive measure
- Can be run on specific tables or all tables

#### Monitoring:
```bash
# Regular health check
python manage.py fix_recipe_sequence --dry-run

# Verbose diagnostics
python manage.py fix_recipe_sequence --dry-run --verbose
```

---

**Updated:** August 2025  
**Purpose:** Fix PostgreSQL sequence synchronization for Recipe system  
**Tables:** recipe_recipe, recipe_recipeingredient  
**Status:** Ready for production use
