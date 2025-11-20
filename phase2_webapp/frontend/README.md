# Healthrix Frontend - React Application

## Quick Start with Create React App

```bash
# Create React app
npx create-react-app healthrix-frontend
cd healthrix-frontend

# Install dependencies
npm install axios react-router-dom @tanstack/react-query
npm install -D tailwindcss postcss autoprefixer

# Set up Tailwind CSS
npx tailwindcss init -p
```

## Recommended Project Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   ├── activities/
│   │   ├── ActivityForm.jsx
│   │   ├── ActivityList.jsx
│   │   └── ActivityCard.jsx
│   ├── performance/
│   │   ├── PerformanceCard.jsx
│   │   ├── TrendChart.jsx
│   │   └── Leaderboard.jsx
│   └── auth/
│       ├── LoginForm.jsx
│       └── RegisterForm.jsx
├── pages/
│   ├── Dashboard.jsx
│   ├── Activities.jsx
│   ├── Performance.jsx
│   └── Login.jsx
├── services/
│   └── api.js              # Axios configuration
├── hooks/
│   └── useAuth.js
├── utils/
│   └── helpers.js
└── App.js
```

## API Configuration

**src/services/api.js**:

```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
};

export const activitiesAPI = {
  list: (params) => api.get('/activities', { params }),
  create: (data) => api.post('/activities', data),
  update: (id, data) => api.put(`/activities/${id}`, data),
  delete: (id) => api.delete(`/activities/${id}`),
};

export const performanceAPI = {
  getScores: (params) => api.get('/performance/scores', { params }),
  getTrend: (empId, startDate, endDate) =>
    api.get(`/performance/trend/${empId}`, { params: { start_date: startDate, end_date: endDate } }),
  getLeaderboard: (date, limit) =>
    api.get('/performance/leaderboard', { params: { target_date: date, limit } }),
  getMyLatest: () => api.get('/performance/my-latest'),
};

export default api;
```

## Environment Variables

Create `.env`:

```
REACT_APP_API_URL=http://localhost:8000
```

## Deployment

### Production Build

```bash
npm run build
```

### Serve with nginx

```nginx
server {
    listen 80;
    server_name healthrix.example.com;

    root /var/www/healthrix/build;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Alternative: Vite + React

For faster development:

```bash
npm create vite@latest healthrix-frontend -- --template react
cd healthrix-frontend
npm install
npm run dev
```

---

For complete frontend implementation, contact the development team or refer to the main documentation.
