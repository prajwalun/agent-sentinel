# Agent Sentinel Dashboard

**Enterprise Security Monitoring Dashboard for AI Agents**

A modern, enterprise-grade web dashboard for visualizing Agent Sentinel monitoring data and security reports. Built with Next.js, TypeScript, and Supabase, featuring a professional black and red theme.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm
- Supabase account (for authentication and data storage)

### Installation

```bash
# Navigate to dashboard directory
cd agent-sentinel-dashboard

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Environment Setup

Create a `.env.local` file in the dashboard directory:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Next.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here

# Google OAuth (if using NextAuth)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Run Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## 🎨 Features

### Authentication & Security
- **Google OAuth** - Single sign-on with Google accounts
- **Supabase Auth** - Secure user authentication and session management
- **Protected Routes** - Automatic route protection for authenticated users
- **Row Level Security** - Data isolation per user/organization

### Real-time Monitoring
- **Live Security Events** - Real-time display of security threats and events
- **Performance Metrics** - Live performance monitoring and analytics
- **Agent Status** - Real-time agent status and health monitoring
- **WebSocket Integration** - Instant updates without page refresh

### Unified Report Visualization
- **Comprehensive Reports** - Visualize complete Agent Sentinel unified reports
- **Executive Summary** - High-level status and risk assessment
- **Threat Analysis** - Detailed breakdown of security threats
- **Performance Charts** - Interactive performance metrics and trends
- **Security Timeline** - Chronological view of security events

### Enterprise Features
- **Black & Red Theme** - Professional, security-focused design
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Export Capabilities** - Export reports as PDF or JSON
- **Multi-tenant Support** - Organization and team management
- **Audit Logging** - Complete audit trail of user actions

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Authentication**: Supabase Auth, NextAuth.js
- **Database**: Supabase PostgreSQL
- **Real-time**: Supabase Realtime
- **Styling**: Tailwind CSS with custom black/red theme
- **Deployment**: Vercel (recommended)

### Project Structure

```
agent-sentinel-dashboard/
├── app/                    # Next.js app directory
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Dashboard pages
│   ├── agents/           # Agent management pages
│   └── reports/          # Report visualization pages
├── components/            # Reusable React components
│   ├── auth/             # Authentication components
│   ├── common/           # Common UI components
│   ├── dashboard/        # Dashboard-specific components
│   ├── agents/           # Agent management components
│   └── reports/          # Report visualization components
├── contexts/             # React contexts
├── hooks/                # Custom React hooks
├── lib/                  # Utility libraries
├── services/             # API and external services
├── types/                # TypeScript type definitions
├── styles/               # Global styles and themes
└── public/               # Static assets
```

## 🔧 Configuration

### Supabase Setup

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Copy your project URL and anon key

2. **Set Up Database Schema**
   ```sql
   -- Run this in Supabase SQL editor
   CREATE TABLE user_profiles (
       id UUID REFERENCES auth.users(id) PRIMARY KEY,
       full_name TEXT,
       company TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   CREATE TABLE agents (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       user_id UUID REFERENCES auth.users(id),
       name TEXT NOT NULL,
       agent_id TEXT UNIQUE NOT NULL,
       status TEXT DEFAULT 'active',
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Enable RLS
   ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
   ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
   ```

3. **Configure Google OAuth**
   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Add redirect URIs to Supabase Auth settings

### Theme Configuration

The dashboard uses a custom black and red theme defined in `tailwind.config.ts`:

```typescript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          black: '#000000',
          'dark-gray': '#1a1a1a',
          'medium-gray': '#2d2d2d',
        },
        accent: {
          red: '#dc2626',
          'warning-red': '#b91c1c',
        },
        status: {
          success: '#059669',
          warning: '#d97706',
          critical: '#dc2626',
        }
      }
    }
  }
}
```

## 📊 Data Integration

### Unified Report Structure

The dashboard visualizes Agent Sentinel unified reports with this structure:

```typescript
interface UnifiedReport {
  agent_id: string;
  start_time: string;
  end_time: string;
  session_logs: LogEntry[];
  security_events: SecurityEvent[];
  performance_metrics: PerformanceMetrics;
  threat_analysis: ThreatAnalysis;
  recommendations: string[];
  summary: {
    status: 'CLEAN' | 'WARNING' | 'CRITICAL';
    risk_score: number;
    threats_detected: number;
    performance_score: number;
  };
}
```

### API Endpoints

```typescript
// Dashboard overview
GET /api/dashboard/overview

// Agent management
GET /api/agents
GET /api/agents/{agentId}

// Reports
GET /api/reports
GET /api/reports/{reportId}

// Authentication
POST /api/auth/login
POST /api/auth/logout
```

## 🎨 Design System

### Color Palette

- **Primary Black**: `#000000` (Main backgrounds)
- **Secondary Black**: `#1a1a1a` (Cards, panels)
- **Dark Gray**: `#2d2d2d` (Borders, dividers)
- **Accent Red**: `#dc2626` (Primary actions, threats)
- **Success Green**: `#059669` (Clean status)
- **Warning Orange**: `#d97706` (Medium risk)
- **White**: `#ffffff` (Primary text)

### Components

- **StatusIndicator** - Shows status with color-coded indicators
- **MetricCard** - Displays metrics with trends
- **EventTimeline** - Shows security events chronologically
- **ReportViewer** - Comprehensive report visualization
- **AuthLayout** - Authentication page layout

## 🚀 Deployment

### Vercel Deployment (Recommended)

1. **Connect to Vercel**
   ```bash
   npm install -g vercel
   vercel login
   vercel
   ```

2. **Set Environment Variables**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add all variables from `.env.local`

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Other Platforms

The dashboard can be deployed to any platform that supports Next.js:

- **Netlify**: Connect your GitHub repository
- **Railway**: Deploy with Railway CLI
- **Docker**: Use the provided Dockerfile

## 🔒 Security

### Authentication Security
- JWT token-based authentication
- Secure cookie storage with httpOnly flags
- CSRF protection
- Rate limiting on authentication endpoints

### Data Protection
- HTTPS only
- Input sanitization
- XSS prevention
- Secure API communication
- Row Level Security (RLS)

## 🧪 Testing

### Run Tests

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
```

### Testing Strategy

- **Unit Tests**: Component and utility function testing
- **Integration Tests**: API and database integration
- **E2E Tests**: Complete user flow testing
- **Visual Tests**: UI consistency and accessibility

## 📈 Performance

### Optimization

- **Next.js 14** - Latest performance optimizations
- **Image Optimization** - Automatic image optimization
- **Code Splitting** - Automatic code splitting
- **Caching** - Strategic caching for better performance

### Monitoring

- **Vercel Analytics** - Built-in performance monitoring
- **Error Tracking** - Sentry integration for error monitoring
- **Real-time Metrics** - Live performance metrics

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Install dependencies**
   ```bash
   npm install
   ```
4. **Make your changes**
5. **Run tests**
   ```bash
   npm run test
   ```
6. **Submit a pull request**

### Code Standards

- **TypeScript** - Strict type checking
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Husky** - Git hooks for quality checks

## 📞 Support

### Documentation

- **[Main Documentation](../README.md)** - Complete project overview
- **[SDK Documentation](../agent-sentinel-sdk/README.md)** - SDK setup and usage
- **[API Reference](../agent-sentinel-sdk/docs/)** - Detailed API documentation

### Community

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Community support and discussions
- **Discord** - Real-time community support

### Enterprise Support

- **Email**: support@agentsentinel.com
- **Enterprise Features**: Custom integrations and deployments
- **Training**: Dedicated training and onboarding

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Agent Sentinel Dashboard** - Visualize your AI agent security monitoring with enterprise-grade insights. 