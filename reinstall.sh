#!/bin/bash

# Script pentru reinstalarea automată a claude-code-session-manager cu pipx
# Utilizare: ./reinstall.sh

set -e

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcții helper
print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verifică dacă pipx este instalat
if ! command -v pipx &> /dev/null; then
    print_error "pipx nu este instalat. Instalează pipx mai întâi:"
    echo "  brew install pipx"
    echo "  pipx ensurepath"
    exit 1
fi

print_step "Reinstalare claude-code-session-manager..."

# Dezinstalează pachetul (ignoră erorile dacă nu există)
print_step "Dezinstalez versiunea curentă..."
if pipx uninstall claude-code-session-manager 2>/dev/null; then
    print_success "Dezinstalare completă"
else
    print_warning "Nu a fost găsit un pachet instalat (normal la prima instalare)"
fi

# Reinstalează din directorul curent
print_step "Instalez versiunea nouă din directorul curent..."
if pipx install .; then
    print_success "Instalare completă"
else
    print_error "Eroare la instalare!"
    exit 1
fi

# Verifică că instalarea a reușit
print_step "Verific instalarea..."
if claude-sessions --help >/dev/null 2>&1; then
    print_success "claude-sessions este disponibil și funcțional"
else
    print_error "claude-sessions nu pare să fie instalat corect"
    exit 1
fi

echo
print_success "Reinstalare completă! Poți folosi 'claude-sessions' din orice director."
echo -e "  Exemplu: ${BLUE}claude-sessions status${NC}"