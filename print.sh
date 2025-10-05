#!/bin/bash

OUTPUT_FILE="output.txt"
exec > "$OUTPUT_FILE" 2>&1

# Directories to include (recursive)
DIRECTORIES=(
  "frontend/src"
  "frontend/public"
  "frontend/src/api"
  "frontend/src/context"
  "frontend/src/hooks"
  "frontend/src/pages"
)

# Individual files to include
FILES=(
  "backend/backend/asgi.py"
  "backend/backend/settings.py"
  "backend/backend/urls.py"
  "backend/backend/wsgi.py"
  "backend/core/admin.py"
  "backend/core/apps.py"
  "backend/core/models.py"
  "backend/core/tests.py"
  "backend/core/urls.py"
  "backend/core/views.py"
  "backend/manage.py"
  "frontend/.gitignore"
  "frontend/eslint.config.js"
  "frontend/index.html"
  "frontend/package.json"
  "frontend/README.md"
  "frontend/vite.config.js"
  "manage.py"
  "README.md"
)

echo "📄 Printing contents of specific files:"
for FILE in "${FILES[@]}"; do
  echo "=============================="
  echo "📦 FILE: $FILE"
  echo "=============================="
  if [ -f "$FILE" ]; then
    cat "$FILE"
  else
    echo "❌ File not found: $FILE"
  fi
  echo ""  # Add spacing between files
done

echo ""
echo "📂 Printing contents of directories:"
for DIR in "${DIRECTORIES[@]}"; do
  if [ -d "$DIR" ]; then
    echo "=============================="
    echo "📁 DIRECTORY: $DIR"
    echo "=============================="
    find "$DIR" -type f -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" \
      -exec echo "📄 {}" \; -exec cat {} \;
  else
    echo "❌ Directory not found: $DIR"
  fi
  echo ""
done

echo "✅ Done. Output written to $OUTPUT_FILE"

