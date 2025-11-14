#!/bin/bash
# Code Quality Check Script
#
# Runs all static analysis tools on the codebase:
# - black (formatting)
# - isort (import sorting)
# - ruff (linting)
# - mypy (type checking)
# - flake8 (style checking)

set -e  # Exit on error

# Get directory where script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
FIX=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: ./scripts/quality.sh [OPTIONS]"
            echo ""
            echo "Run code quality checks on the codebase."
            echo ""
            echo "Options:"
            echo "  --fix       Automatically fix formatting and import issues"
            echo "  --check     Only check, don't modify files (CI mode)"
            echo "  --help      Show this help message"
            echo ""
            echo "Tools used:"
            echo "  - black:    Code formatting"
            echo "  - isort:    Import sorting"
            echo "  - ruff:     Fast linting (replaces flake8 + more)"
            echo "  - mypy:     Static type checking"
            echo "  - flake8:   Additional style checking"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Code Quality Analysis${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counter for issues
ISSUES=0

# 1. Black - Code formatting
echo -e "${YELLOW}[1/5] Running Black (code formatting)...${NC}"
if [ "$FIX" = true ]; then
    if poetry run black pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Black formatting applied${NC}"
    else
        echo -e "${RED}✗ Black failed${NC}"
        ((ISSUES++))
    fi
elif [ "$CHECK_ONLY" = true ]; then
    if poetry run black --check pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Black formatting check passed${NC}"
    else
        echo -e "${RED}✗ Black formatting check failed${NC}"
        echo -e "${YELLOW}  Run with --fix to automatically format${NC}"
        ((ISSUES++))
    fi
else
    if poetry run black --check --diff pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Black formatting check passed${NC}"
    else
        echo -e "${RED}✗ Black formatting issues found${NC}"
        echo -e "${YELLOW}  Run with --fix to automatically format${NC}"
        ((ISSUES++))
    fi
fi
echo ""

# 2. isort - Import sorting
echo -e "${YELLOW}[2/5] Running isort (import sorting)...${NC}"
if [ "$FIX" = true ]; then
    if poetry run isort pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Import sorting applied${NC}"
    else
        echo -e "${RED}✗ isort failed${NC}"
        ((ISSUES++))
    fi
elif [ "$CHECK_ONLY" = true ]; then
    if poetry run isort --check-only pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Import sorting check passed${NC}"
    else
        echo -e "${RED}✗ Import sorting check failed${NC}"
        echo -e "${YELLOW}  Run with --fix to automatically sort imports${NC}"
        ((ISSUES++))
    fi
else
    if poetry run isort --check-only --diff pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Import sorting check passed${NC}"
    else
        echo -e "${RED}✗ Import sorting issues found${NC}"
        echo -e "${YELLOW}  Run with --fix to automatically sort imports${NC}"
        ((ISSUES++))
    fi
fi
echo ""

# 3. Ruff - Fast linting
echo -e "${YELLOW}[3/5] Running Ruff (fast linting)...${NC}"
if [ "$FIX" = true ]; then
    if poetry run ruff check --fix pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Ruff linting issues fixed${NC}"
    else
        echo -e "${RED}✗ Ruff found unfixable issues${NC}"
        ((ISSUES++))
    fi
else
    if poetry run ruff check pytaiga_mcp/ tests/; then
        echo -e "${GREEN}✓ Ruff linting passed${NC}"
    else
        echo -e "${RED}✗ Ruff linting issues found${NC}"
        echo -e "${YELLOW}  Run with --fix to automatically fix some issues${NC}"
        ((ISSUES++))
    fi
fi
echo ""

# 4. mypy - Type checking
echo -e "${YELLOW}[4/5] Running mypy (type checking)...${NC}"
if poetry run mypy pytaiga_mcp/; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${RED}✗ Type checking issues found${NC}"
    ((ISSUES++))
fi
echo ""

# 5. flake8 - Style checking
echo -e "${YELLOW}[5/5] Running flake8 (style checking)...${NC}"
if poetry run flake8 pytaiga_mcp/ tests/; then
    echo -e "${GREEN}✓ Style checking passed${NC}"
else
    echo -e "${RED}✗ Style checking issues found${NC}"
    ((ISSUES++))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All quality checks passed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    exit 0
else
    echo -e "${RED}✗ Found issues in $ISSUES tool(s)${NC}"
    echo -e "${BLUE}========================================${NC}"
    if [ "$FIX" != true ]; then
        echo -e "${YELLOW}Tip: Run with --fix to automatically fix formatting and import issues${NC}"
    fi
    exit 1
fi
