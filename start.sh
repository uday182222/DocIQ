#!/bin/bash

# DocIQ Production Startup Script
# This script starts both the backend API server and frontend React application

set -e  # Exit on any error

echo "🚀 Starting DocIQ: Smart Document Parser"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the dociq-ui directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

print_status "Checking dependencies..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found. Installing..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies found"
fi

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_warning "Backend virtual environment not found. Creating..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    print_success "Backend virtual environment created and dependencies installed"
else
    print_success "Backend virtual environment found"
fi

# Check for environment file
if [ ! -f "backend/.env" ]; then
    print_warning "No .env file found in backend directory"
    print_status "Creating .env file with mock mode enabled..."
    echo "USE_MOCK_GEMINI=true" > backend/.env
    print_status "To use real Gemini AI, edit backend/.env and add your GEMINI_API_KEY"
fi

print_status "Starting services..."

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
print_status "Starting backend API server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

print_success "Backend API server started (PID: $BACKEND_PID)"

# Start frontend
print_status "Starting frontend React application..."
npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

print_success "Frontend React application started (PID: $FRONTEND_PID)"

echo ""
print_success "🎉 DocIQ is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop the services
wait 