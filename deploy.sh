#!/bin/bash

# 🚀 Agno Bot Railway Deployment Script
# This script helps you deploy your Agno Bot to Railway

echo "🤖 Agno Bot Railway Deployment Script"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway..."
    railway login
fi

echo "📋 Prerequisites Check:"
echo "✅ Railway CLI installed"
echo "✅ Logged in to Railway"

echo ""
echo "🚀 Starting Deployment Process..."
echo ""

# Step 1: Initialize Railway project (if not already done)
echo "1️⃣ Initializing Railway project..."
if [ ! -f "railway.json" ]; then
    echo "📝 Creating railway.json..."
    railway init
else
    echo "✅ railway.json already exists"
fi

# Step 2: Deploy backend
echo ""
echo "2️⃣ Deploying Backend..."
cd backend
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🚀 Deploying to Railway..."
railway up

echo "✅ Backend deployed successfully!"
cd ..

# Step 3: Deploy frontend
echo ""
echo "3️⃣ Deploying Frontend..."
cd frontend
echo "📦 Installing Node.js dependencies..."
npm install

echo "🏗️ Building frontend..."
npm run build

echo "🚀 Deploying to Railway..."
railway up

echo "✅ Frontend deployed successfully!"
cd ..

# Step 4: Get deployment URLs
echo ""
echo "4️⃣ Getting Deployment URLs..."
echo "🔍 Checking deployment status..."

BACKEND_URL=$(railway status --service backend 2>/dev/null | grep -o 'https://[^[:space:]]*' || echo "https://your-backend-service.railway.app")
FRONTEND_URL=$(railway status --service frontend 2>/dev/null | grep -o 'https://[^[:space:]]*' || echo "https://your-frontend-service.railway.app")

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🔗 Your Application URLs:"
echo "   Backend API: $BACKEND_URL"
echo "   Frontend App: $FRONTEND_URL"
echo "   API Docs: $BACKEND_URL/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Update your FINAL_SUBMISSION.md with the actual URLs"
echo "   2. Create a demo video using Loom or YouTube"
echo "   3. Create an architecture diagram using Figma or Miro"
echo "   4. Test your deployed application"
echo ""
echo "🔧 Environment Variables to Set in Railway:"
echo "   DATABASE_URL=postgresql://..."
echo "   GEMINI_API_KEY=your_gemini_api_key"
echo "   ZEP_API_KEY=your_zep_api_key"
echo "   MEM0_API_KEY=your_mem0_api_key"
echo "   SECRET_KEY=your_secret_key"
echo "   CORS_ORIGINS=[\"$FRONTEND_URL\"]"
echo ""
echo "📚 Useful Commands:"
echo "   railway logs --service backend    # View backend logs"
echo "   railway logs --service frontend   # View frontend logs"
echo "   railway variables                 # Manage environment variables"
echo "   railway status                    # Check deployment status"
echo ""
echo "🎯 Your Agno Bot is now live at: $FRONTEND_URL" 