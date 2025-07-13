# Agent Sentinel Dashboard - Frontend Design Specification

## Project Overview
Build a professional, enterprise-grade dashboard for Agent Sentinel using Vercel v0. The dashboard should display unified monitoring reports, security events, performance metrics, and provide actionable insights for AI agent security monitoring.

## Design Theme & Branding

### Color Palette - Enterprise Black & Red Theme
- **Primary Black**: `#000000` (Main background, text)
- **Secondary Black**: `#1a1a1a` (Cards, panels)
- **Dark Gray**: `#2d2d2d` (Borders, dividers)
- **Medium Gray**: `#4a4a4a` (Secondary text)
- **Light Gray**: `#6b6b6b` (Placeholder text)
- **Accent Red**: `#dc2626` (Primary accent, threats, CTAs)
- **Warning Red**: `#b91c1c` (Darker red for hover states)
- **Success Green**: `#059669` (Clean status, success)
- **Warning Orange**: `#d97706` (Medium risk, warnings)
- **White**: `#ffffff` (Primary text on dark backgrounds)
- **Off-White**: `#f8f8f8` (Secondary text on dark backgrounds)

### Typography
- **Primary Font**: Inter (Clean, modern, highly readable)
- **Code Font**: JetBrains Mono (For technical data)
- **Font Weights**: 400 (Regular), 500 (Medium), 600 (Semi-bold), 700 (Bold)

### Design System
- **Border Radius**: 8px (Cards), 4px (Buttons, inputs)
- **Shadows**: Subtle elevation with `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3)`
- **Spacing**: 8px grid system (8px, 16px, 24px, 32px, 48px, 64px)
- **Theme**: Dark mode by default, with option for light mode

## Authentication Pages

### 1. Login Page

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│                    🛡️ Agent Sentinel                       │
│                                                             │
│              Enterprise Security Monitoring                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Sign In to Your Dashboard                          │   │
│  │                                                     │   │
│  │ Email Address                                      │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ Password                                           │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ [✓] Remember me                                    │   │
│  │                                                     │   │
│  │ [Sign In]                                          │   │
│  │                                                     │   │
│  │ Forgot password? [Reset]                           │   │
│  │                                                     │   │
│  │ Don't have an account? [Sign Up]                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Design Elements:**
- **Background**: Gradient from black to dark gray
- **Card**: Dark gray background with subtle red border
- **Input Fields**: Black background with red focus states
- **Button**: Red background with white text
- **Logo**: White shield icon with red accent

### 2. Sign Up Page

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│                    🛡️ Agent Sentinel                       │
│                                                             │
│              Enterprise Security Monitoring                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Create Your Account                                │   │
│  │                                                     │   │
│  │ Full Name                                          │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ Company/Organization                               │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ Email Address                                      │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ Password                                           │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ Confirm Password                                   │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ [✓] I agree to Terms of Service                    │   │
│  │ [✓] I want to receive security updates             │   │
│  │                                                     │   │
│  │ [Create Account]                                   │   │
│  │                                                     │   │
│  │ Already have an account? [Sign In]                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Password Reset Page

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│                    🛡️ Agent Sentinel                       │
│                                                             │
│              Enterprise Security Monitoring                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Reset Your Password                                │   │
│  │                                                     │   │
│  │ Enter your email address and we'll send you        │   │
│  │ a link to reset your password.                     │   │
│  │                                                     │   │
│  │ Email Address                                      │   │
│  │ [________________________]                         │   │
│  │                                                     │   │
│  │ [Send Reset Link]                                  │   │
│  │                                                     │   │
│  │ [← Back to Sign In]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. Email Verification Page

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│                    🛡️ Agent Sentinel                       │
│                                                             │
│              Enterprise Security Monitoring                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Verify Your Email                                  │   │
│  │                                                     │   │
│  │ We've sent a verification link to:                 │   │
│  │ user@company.com                                   │   │
│  │                                                     │   │
│  │ Please check your email and click the link to      │   │
│  │ verify your account.                               │   │
│  │                                                     │   │
│  │ [Resend Email]                                     │   │
│  │                                                     │   │
│  │ [Change Email Address]                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Layout Structure

### Main Layout (Desktop) - Dark Theme
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo + Navigation + User Menu (Black background)   │
├─────────────────────────────────────────────────────────────┤
│ Sidebar: Dashboard | Agents | Reports | Settings (Dark)     │
├─────────────────────────────────────────────────────────────┤
│ Main Content Area (Black background)                       │
│ ┌─────────────┬─────────────┬─────────────┐                │
│ │ Status Card │ Metrics     │ Quick Stats │ (Dark cards)   │
│ └─────────────┴─────────────┴─────────────┘                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Main Content (Reports, Agent Details, etc.)            │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Mobile Layout - Dark Theme
```
┌─────────────────────────────────────┐
│ Header: Logo + Hamburger Menu       │
├─────────────────────────────────────┤
│ Main Content (Stacked Dark Cards)   │
│ ┌─────────────────────────────────┐ │
│ │ Status Overview                │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ Agent List                     │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ Recent Reports                 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Page Wireframes - Dark Theme

### 1. Dashboard Overview Page

**Header Section:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ Agent Sentinel    [Dashboard] [Agents] [Reports] [Settings] │
│                                                             │
│ User: John Doe | [Profile] [Logout]                        │
└─────────────────────────────────────────────────────────────┘
```

**Status Overview Cards (Dark Cards with Red Accents):**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Agents│ Active      │ Threats     │ Performance │
│    12       │    8        │    3        │   95.2%     │
│   +2 today  │   +1 today  │   +1 today  │   +2.1%     │
│  (Red text) │ (Green text)│ (Red text)  │(Green text) │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Recent Activity Feed (Dark Background):**
```
┌─────────────────────────────────────────────────────────────┐
│ Recent Activity                                             │
├─────────────────────────────────────────────────────────────┤
│ 🔴 2 min ago: SQL injection detected in Agent "DataBot"     │
│ 🟡 5 min ago: Performance warning in Agent "ChatBot"        │
│ 🟢 12 min ago: Agent "MathAgent" completed successfully     │
│ 🔴 15 min ago: XSS attempt blocked in Agent "WebBot"        │
└─────────────────────────────────────────────────────────────┘
```

**Quick Actions:**
```
┌─────────────────────────────────────────────────────────────┐
│ Quick Actions                                               │
├─────────────────────────────────────────────────────────────┤
│ [📊 Generate Report] [🔍 View All Agents] [⚙️ Settings]     │
│ (Red buttons with white text)                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Agent Details Page

**Agent Header:**
```
┌─────────────────────────────────────────────────────────────┐
│ Agent: MathAgent                    Status: 🟢 ACTIVE       │
│ Created: 2025-07-13 | Last Active: 2 minutes ago            │
│                                                             │
│ [Edit Agent] [Generate Report] [Delete Agent]               │
│ (Red buttons)                                               │
└─────────────────────────────────────────────────────────────┘
```

**Agent Metrics (Dark Cards):**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Calls Today │ Avg Response│ Error Rate  │ Security    │
│    156      │   245ms     │   0.2%      │   CLEAN     │
│ (White text)│ (White text)│ (Green text)│(Green text) │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Security Events Timeline (Dark Background):**
```
┌─────────────────────────────────────────────────────────────┐
│ Security Events (Last 24h)                                 │
├─────────────────────────────────────────────────────────────┤
│ 14:30 - 🟢 Function call: process_data()                   │
│ 14:25 - 🟢 Function call: calculate_sum()                  │
│ 14:20 - 🟡 Warning: High memory usage detected             │
│ 14:15 - 🟢 Function call: validate_input()                 │
└─────────────────────────────────────────────────────────────┘
```

### 3. Unified Report Viewer

**Report Header:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📋 Unified Report: MathAgent_20250713_021239               │
│ Generated: 2025-07-13 02:12:39 | Status: 🟢 CLEAN          │
│                                                             │
│ [Export PDF] [Share Report] [Print]                        │
│ (Red buttons)                                               │
└─────────────────────────────────────────────────────────────┘
```

**Executive Summary (Dark Card):**
```
┌─────────────────────────────────────────────────────────────┐
│ Executive Summary                                           │
├─────────────────────────────────────────────────────────────┤
│ Overall Status: 🟢 CLEAN                                    │
│ Risk Score: 12/100 (Low Risk)                              │
│ Threats Detected: 0                                         │
│ Performance: Excellent (95.2%)                             │
│ Recommendations: 2                                          │
└─────────────────────────────────────────────────────────────┘
```

**Detailed Sections (Collapsible Dark Cards):**
```
┌─────────────────────────────────────────────────────────────┐
│ ▼ Threat Analysis (0 threats)                              │
├─────────────────────────────────────────────────────────────┤
│ No security threats detected during this session.          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ▼ Performance Metrics                                       │
├─────────────────────────────────────────────────────────────┤
│ Response Time: 245ms avg | Memory Usage: 45MB              │
│ Function Calls: 156 | Success Rate: 99.8%                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ▼ Security Events (156 events)                             │
├─────────────────────────────────────────────────────────────┤
│ [Detailed event list with timestamps and descriptions]     │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Authentication Components

**Login Form:**
```typescript
interface LoginFormProps {
  onSubmit: (email: string, password: string, rememberMe: boolean) => void;
  onForgotPassword: () => void;
  onSignUp: () => void;
  loading?: boolean;
  error?: string;
}
```

**Sign Up Form:**
```typescript
interface SignUpFormProps {
  onSubmit: (userData: {
    fullName: string;
    company: string;
    email: string;
    password: string;
    confirmPassword: string;
    termsAccepted: boolean;
    marketingAccepted: boolean;
  }) => void;
  onSignIn: () => void;
  loading?: boolean;
  error?: string;
}
```

**Password Reset Form:**
```typescript
interface PasswordResetFormProps {
  onSubmit: (email: string) => void;
  onBackToSignIn: () => void;
  loading?: boolean;
  success?: boolean;
  error?: string;
}
```

### 2. Status Indicator Component
```typescript
interface StatusIndicatorProps {
  status: 'clean' | 'warning' | 'critical';
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
}
```

**Visual Design (Dark Theme):**
- Clean: Green circle with checkmark
- Warning: Orange triangle with exclamation
- Critical: Red circle with X
- Background: Dark gray cards
- Text: White/off-white

### 3. Metric Card Component
```typescript
interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  color?: 'red' | 'green' | 'orange' | 'gray';
  trend?: {
    direction: 'up' | 'down' | 'stable';
    value: string;
    period: string;
  };
}
```

### 4. Event Timeline Component
```typescript
interface EventTimelineProps {
  events: Array<{
    timestamp: string;
    type: 'security' | 'performance' | 'info';
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    agentId?: string;
  }>;
  maxEvents?: number;
}
```

### 5. Report Viewer Component
```typescript
interface ReportViewerProps {
  reportData: {
    agent_id: string;
    start_time: string;
    end_time: string;
    executive_summary: {
      status: string;
      risk_score: number;
      threats_detected: number;
      performance_score: number;
    };
    security_events: SecurityEvent[];
    performance_metrics: PerformanceMetrics;
    recommendations: Recommendation[];
  };
}
```

## Data Integration

### Authentication API Endpoints
```typescript
// Authentication
POST /api/auth/login
{
  email: string;
  password: string;
  rememberMe?: boolean;
}

POST /api/auth/signup
{
  fullName: string;
  company: string;
  email: string;
  password: string;
  confirmPassword: string;
  termsAccepted: boolean;
  marketingAccepted: boolean;
}

POST /api/auth/forgot-password
{
  email: string;
}

POST /api/auth/reset-password
{
  token: string;
  password: string;
  confirmPassword: string;
}

POST /api/auth/verify-email
{
  token: string;
}

POST /api/auth/logout
```

### Dashboard API Endpoints
```typescript
// Dashboard overview
GET /api/dashboard/overview
{
  totalAgents: number;
  activeAgents: number;
  threatsToday: number;
  performanceScore: number;
  recentActivity: ActivityEvent[];
}

// Agent list
GET /api/agents
{
  agents: Array<{
    id: string;
    name: string;
    status: 'active' | 'inactive' | 'error';
    lastActive: string;
    threatCount: number;
    performanceScore: number;
  }>;
}

// Agent details
GET /api/agents/{agentId}
{
  agent: AgentDetails;
  metrics: AgentMetrics;
  recentEvents: SecurityEvent[];
}

// Reports
GET /api/reports
{
  reports: Array<{
    id: string;
    agentId: string;
    generatedAt: string;
    status: string;
    riskScore: number;
  }>;
}

GET /api/reports/{reportId}
{
  // Full unified report data
}
```

## Responsive Design Requirements

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Mobile Adaptations
- Stack all cards vertically
- Use hamburger menu for navigation
- Collapse detailed sections by default
- Optimize touch targets (min 44px)
- Use larger text for readability
- Dark theme optimized for mobile screens

### Tablet Adaptations
- 2-column grid for metric cards
- Sidebar becomes collapsible
- Maintain desktop layout with adjusted spacing
- Dark theme with proper contrast

## Interactive Features

### 1. Authentication Flow
- Form validation with real-time feedback
- Password strength indicator
- Email verification flow
- Remember me functionality
- Forgot password with email reset
- Social login options (optional)

### 2. Real-time Updates
- WebSocket connection for live event streaming
- Auto-refresh dashboard metrics every 30 seconds
- Push notifications for critical security events
- Real-time status indicators

### 3. Filtering & Search
- Search agents by name or ID
- Filter events by type, severity, time range
- Sort reports by date, status, risk score
- Advanced filtering options

### 4. Export & Sharing
- Export reports as PDF/JSON
- Share dashboard links with team members
- Email notifications for critical events
- Scheduled report generation

### 5. Drill-down Navigation
- Click agent cards → Agent details page
- Click events → Event details modal
- Click metrics → Performance analysis page
- Breadcrumb navigation

## Accessibility Requirements

### WCAG 2.1 AA Compliance
- Color contrast ratio: 4.5:1 minimum (optimized for dark theme)
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators for all interactive elements
- Alt text for all images and icons

### Semantic HTML
- Proper heading hierarchy (h1-h6)
- ARIA labels for complex components
- Form labels and descriptions
- Error messages and validation feedback

## Performance Requirements

### Loading Times
- Initial page load: < 2 seconds
- Dashboard metrics: < 1 second
- Report generation: < 3 seconds
- Authentication: < 1 second
- Image optimization and lazy loading

### Caching Strategy
- Static assets: 1 year
- API responses: 5 minutes
- User preferences: Local storage
- Report data: Session storage
- Authentication tokens: Secure storage

## Security Considerations

### Authentication Security
- JWT token-based authentication
- Secure cookie storage with httpOnly flags
- CSRF protection
- Rate limiting on authentication endpoints
- Password hashing and salting
- Email verification required

### Data Protection
- HTTPS only
- Input sanitization
- XSS prevention
- Secure API communication
- Session management
- Audit logging

## Testing Strategy

### Component Testing
- Unit tests for all React components
- Integration tests for API interactions
- E2E tests for critical user flows
- Authentication flow testing

### Visual Testing
- Screenshot testing for UI consistency
- Cross-browser compatibility testing
- Mobile device testing
- Dark theme testing

## Deployment & CI/CD

### Vercel Configuration
- Automatic deployments on git push
- Preview deployments for pull requests
- Environment variable management
- Custom domain setup
- Edge functions for API routes

### Monitoring
- Error tracking with Sentry
- Performance monitoring
- User analytics
- Uptime monitoring
- Authentication analytics

## File Structure Recommendation

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── SignUpForm.tsx
│   │   ├── PasswordResetForm.tsx
│   │   ├── EmailVerification.tsx
│   │   └── AuthLayout.tsx
│   ├── common/
│   │   ├── StatusIndicator.tsx
│   │   ├── MetricCard.tsx
│   │   ├── EventTimeline.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ThemeToggle.tsx
│   ├── dashboard/
│   │   ├── DashboardOverview.tsx
│   │   ├── StatusCards.tsx
│   │   └── RecentActivity.tsx
│   ├── agents/
│   │   ├── AgentList.tsx
│   │   ├── AgentCard.tsx
│   │   └── AgentDetails.tsx
│   └── reports/
│       ├── ReportList.tsx
│       ├── ReportViewer.tsx
│       └── ReportExport.tsx
├── pages/
│   ├── auth/
│   │   ├── login.tsx
│   │   ├── signup.tsx
│   │   ├── forgot-password.tsx
│   │   └── verify-email.tsx
│   ├── dashboard/
│   ├── agents/
│   └── reports/
├── hooks/
│   ├── useAuth.ts
│   ├── useAgents.ts
│   ├── useReports.ts
│   └── useWebSocket.ts
├── services/
│   ├── auth.ts
│   ├── api.ts
│   └── websocket.ts
├── types/
│   ├── auth.ts
│   ├── agent.ts
│   ├── report.ts
│   └── event.ts
├── utils/
│   ├── auth.ts
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
├── styles/
│   ├── globals.css
│   ├── components.css
│   ├── themes.css
│   └── auth.css
└── contexts/
    ├── AuthContext.tsx
    └── ThemeContext.tsx
```

## Implementation Priority

### Phase 1: Authentication & Core Setup (Week 1)
1. Authentication pages (Login, Sign Up, Password Reset)
2. Authentication context and hooks
3. Protected routes and middleware
4. Basic layout and navigation
5. Dark theme implementation

### Phase 2: Dashboard Foundation (Week 2)
1. Dashboard overview page
2. Status cards and metrics
3. Basic agent list
4. Authentication integration
5. Real-time updates setup

### Phase 3: Agent Management (Week 3)
1. Agent details pages
2. Event timeline
3. Performance metrics
4. Search and filtering
5. Agent CRUD operations

### Phase 4: Reporting & Advanced Features (Week 4)
1. Report list and viewer
2. Unified report display
3. Export functionality
4. Advanced filtering
5. Mobile optimization

## Success Metrics

### User Experience
- Page load time < 2 seconds
- Authentication success rate > 95%
- Zero critical accessibility issues
- 95%+ cross-browser compatibility
- Mobile usability score > 90

### Business Metrics
- User registration conversion > 70%
- Dashboard adoption rate > 80%
- Average session duration > 5 minutes
- Report generation usage > 60%
- User satisfaction score > 4.5/5

## Theme Instructions for Vercel v0

### Critical Theme Requirements
- **NO BLUE COLORS**: Avoid any blue colors in the design
- **Primary Theme**: Black and red enterprise theme
- **Background**: Pure black (#000000) for main backgrounds
- **Cards**: Dark gray (#1a1a1a) for content cards
- **Accent Color**: Red (#dc2626) for primary actions and threats
- **Text**: White (#ffffff) for primary text on dark backgrounds
- **Status Colors**: 
  - Success: Green (#059669)
  - Warning: Orange (#d97706)
  - Critical: Red (#dc2626)

### Design Guidelines
- Use high contrast for accessibility
- Implement proper focus states with red accents
- Ensure all interactive elements are clearly visible
- Maintain professional enterprise appearance
- Avoid any blue color variations

This specification provides a comprehensive foundation for building a professional, enterprise-grade dashboard with authentication that effectively displays Agent Sentinel's unified monitoring data using a distinctive black and red theme. 