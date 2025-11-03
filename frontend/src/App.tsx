import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/es/locale/zh_CN';
import 'antd/dist/antd.css';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import StudyPlansPage from './pages/StudyPlansPage';
import ErrorLogsPage from './pages/ErrorLogsPage';
import ConversationsPage from './pages/ConversationsPage';
import ProfilePage from './pages/ProfilePage';
import AIStudyPlanPage from './pages/AIStudyPlanPage';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={zhCN}>
        <Router>
          <div className="App">
            <Routes>
              {/* 公开路由 */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* 受保护的路由 */}
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/study-plans" element={<StudyPlansPage />} />
                        <Route path="/ai-study-plan" element={<AIStudyPlanPage />} />
                        <Route path="/error-logs" element={<ErrorLogsPage />} />
                        <Route path="/conversations" element={<ConversationsPage />} />
                        <Route path="/profile" element={<ProfilePage />} />
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;
