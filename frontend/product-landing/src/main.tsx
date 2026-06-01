import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Models from './pages/Models';
import Docs from './pages/Docs';
import QuickStart from './pages/docs/QuickStart';
import ModelsAndPricing from './pages/docs/ModelsAndPricing';
import TokenUsage from './pages/docs/TokenUsage';
import RateLimits from './pages/docs/RateLimits';
import ErrorCodes from './pages/docs/ErrorCodes';
import CreateChatCompletion from './pages/docs/CreateChatCompletion';
import ListModels from './pages/docs/ListModels';
import GetBalance from './pages/docs/GetBalance';
import AdminDashboard from './pages/admin/Dashboard';
import APIKeys from './pages/admin/APIKeys';
import TopUp from './pages/admin/TopUp';
import BillingHistory from './pages/admin/BillingHistory';
import BillingDetail from './pages/admin/BillingDetail';
import './styles/index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/models" element={<Models />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/docs/quick-start" element={<QuickStart />} />
          <Route path="/docs/models" element={<ModelsAndPricing />} />
          <Route path="/docs/token-usage" element={<TokenUsage />} />
          <Route path="/docs/rate-limits" element={<RateLimits />} />
          <Route path="/docs/error-codes" element={<ErrorCodes />} />
          <Route path="/docs/create-chat-completion" element={<CreateChatCompletion />} />
          <Route path="/docs/list-models" element={<ListModels />} />
          <Route path="/docs/get-balance" element={<GetBalance />} />
        </Route>
        <Route path="/admin" element={<Layout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="api-keys" element={<APIKeys />} />
          <Route path="top-up" element={<TopUp />} />
          <Route path="billing" element={<BillingHistory />} />
          <Route path="billing/:id" element={<BillingDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
