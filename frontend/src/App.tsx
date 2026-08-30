import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { UserAnalysis } from './pages/UserAnalysis';
import { NetworkAnalysis } from './pages/NetworkAnalysis';
import { Communities } from './pages/Communities';
import { Coordination } from './pages/Coordination';
import { ModelPerformance } from './pages/ModelPerformance';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/users" element={<UserAnalysis />} />
          <Route path="/users/:id" element={<UserAnalysis />} />
          <Route path="/network" element={<NetworkAnalysis />} />
          <Route path="/communities" element={<Communities />} />
          <Route path="/communities/:id" element={<Communities />} />
          <Route path="/coordination" element={<Coordination />} />
          <Route path="/model-performance" element={<ModelPerformance />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
