# 🚀 Railway Deployment Guide

This guide will help you deploy Agno Bot to Railway and set up all the necessary links for your final submission.

## 📋 Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **API Keys**: 
   - Google Gemini AI API key
   - Zep AI API key
   - Mem0 API key

## 🚀 Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository has the following structure:
```
agno-bot/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── railway.json
│   └── run.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── public/
├── README.md
├── TECHNICAL_REPORT.md
└── DEPLOYMENT_GUIDE.md
```

### 2. Deploy Backend to Railway

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Click "New Project"

2. **Connect GitHub Repository**
   - Select "Deploy from GitHub repo"
   - Choose your `agno-bot` repository
   - Select the `backend` directory as the source

3. **Configure Environment Variables**
   Add these variables in Railway:
   ```env
   DATABASE_URL=postgresql://...  # Railway will provide this
   GEMINI_API_KEY=your_gemini_api_key
   ZEP_API_KEY=your_zep_api_key
   MEM0_API_KEY=your_mem0_api_key
   SECRET_KEY=your_secure_secret_key
   CORS_ORIGINS=["https://your-frontend-domain.railway.app"]
   DEBUG=False
   LOG_LEVEL=INFO
   ```

4. **Deploy**
   - Railway will automatically detect the Python app
   - It will use the `Dockerfile` and `railway.json` for configuration
   - Wait for deployment to complete

### 3. Deploy Frontend to Railway

1. **Create New Service**
   - In the same Railway project, click "New Service"
   - Select "Deploy from GitHub repo"
   - Choose your `agno-bot` repository
   - Select the `frontend` directory

2. **Configure Frontend**
   - Railway will automatically detect it's a React app
   - Set the build command: `npm run build`
   - Set the start command: `npx serve -s build -l $PORT`

3. **Update API URL**
   - In `frontend/src/api.js`, update the API_BASE_URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-domain.railway.app';
   ```

4. **Deploy**
   - Railway will build and deploy the frontend
   - Wait for deployment to complete

### 4. Set Up Database

1. **Add PostgreSQL Service**
   - In Railway project, click "New Service"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically create the database

2. **Connect Backend to Database**
   - Copy the PostgreSQL connection URL
   - Add it as `DATABASE_URL` in your backend environment variables

### 5. Configure Domains

1. **Get Your URLs**
   - Backend: `https://your-backend-service.railway.app`
   - Frontend: `https://your-frontend-service.railway.app`
   - Database: Managed by Railway

2. **Update CORS Settings**
   - In backend environment variables, update:
   ```env
   CORS_ORIGINS=["https://your-frontend-service.railway.app"]
   ```

## 📹 Create Demo Video

### Using Loom (Recommended)

1. **Sign up at [loom.com](https://loom.com)**
2. **Record your demo**:
   - Show the application features
   - Demonstrate chat functionality
   - Show memory systems working
   - Display the architecture
3. **Share the video** and get the share link

### Alternative: YouTube

1. Upload your demo video to YouTube
2. Set it to "Unlisted" for privacy
3. Share the YouTube link

## 🏗️ Create Architecture Diagram

### Using Figma

1. **Sign up at [figma.com](https://figma.com)**
2. **Create architecture diagram**:
   - System components
   - Data flow
   - Technology stack
3. **Share the file** and get the share link

### Alternative: Miro

1. Use [miro.com](https://miro.com) for collaborative diagrams
2. Create your architecture diagram
3. Share the board link

## 📝 Final Submission Checklist

### ✅ Required Links

1. **Repository Link**: `https://github.com/[your-username]/agno-bot`
2. **Live Bot URL**: `https://[your-app].railway.app`
3. **Demo Video**: `https://loom.com/share/[video-id]`
4. **Architecture Diagram**: `https://figma.com/file/[file-id]`
5. **Technical Report**: Included in repo as `TECHNICAL_REPORT.md`

### ✅ Documentation Files

- [x] `README.md` - Comprehensive project documentation
- [x] `TECHNICAL_REPORT.md` - Technical implementation details
- [x] `DEPLOYMENT_GUIDE.md` - This deployment guide
- [x] `backend/railway.json` - Railway configuration
- [x] `backend/Dockerfile` - Container configuration

### ✅ Code Quality

- [x] Clean, well-documented code
- [x] Proper error handling
- [x] Security best practices
- [x] Performance optimizations
- [x] Comprehensive testing

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for all dependencies
   - Verify Python version compatibility
   - Check for syntax errors

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correct
   - Check if database service is running
   - Ensure tables are created

3. **CORS Errors**
   - Update `CORS_ORIGINS` with correct frontend URL
   - Restart backend service after changes

4. **API Key Issues**
   - Verify all API keys are valid
   - Check API quotas and limits
   - Ensure proper environment variable names

### Getting Help

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Create an issue in your repository

## 🎉 Success!

Once deployed, your application will be available at:
- **Frontend**: `https://your-frontend-service.railway.app`
- **Backend API**: `https://your-backend-service.railway.app`
- **API Docs**: `https://your-backend-service.railway.app/docs`

## 📊 Monitoring

Railway provides built-in monitoring:
- **Logs**: View application logs in real-time
- **Metrics**: Monitor CPU, memory, and network usage
- **Health Checks**: Automatic health monitoring
- **Deployments**: Track deployment history

## 🔄 Continuous Deployment

Railway automatically deploys when you push to your main branch:
1. Push changes to GitHub
2. Railway detects the changes
3. Automatic build and deployment
4. Zero-downtime updates

---

**🎯 Your Agno Bot is now ready for production!** 