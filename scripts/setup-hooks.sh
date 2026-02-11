#!/bin/bash
# Setup script to install Git hooks

set -e

echo "🔧 Installing Git hooks..."

# Copy pre-commit hook
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✓ Pre-commit hook installed"
echo ""
echo "This hook will:"
echo "  - Run ruff check on staged Python files before commit"
echo "  - Block commits if lint errors are found"
echo "  - Skip with: git commit --no-verify (use sparingly!)"
echo ""
echo "🎉 Setup complete!"
