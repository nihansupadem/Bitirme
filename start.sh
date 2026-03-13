#!/bin/bash
# OpTrade — Start the local PHP development server
# Usage: bash start.sh   (from inside BIST_PROJECT folder)

PORT=8080
DIR="$(cd "$(dirname "$0")" && pwd)/backend/frontend"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   📈  OpTrade — Local Development Server      ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""
echo "  Serving from: $DIR"
echo "  URL:          http://localhost:$PORT"
echo ""
echo "  Pages:"
echo "    http://localhost:$PORT/index.php      ← Main analysis"
echo "    http://localhost:$PORT/auth.php       ← Sign in / Sign up"
echo "    http://localhost:$PORT/dashboard.php  ← Your dashboard"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Kill any existing PHP server on this port
lsof -ti :$PORT | xargs kill -9 2>/dev/null

# Start the server
cd "$DIR" && php -S localhost:$PORT
