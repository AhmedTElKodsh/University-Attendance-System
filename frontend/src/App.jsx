{ BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authService } from './services/api';

// Pages
import Login from './pages/Login';
import AdminDashboard from './pages/admin/Dashboard';
import StudentManagement from './pages/admin/StudentManagement';
import DoctorManagement from './pages/admin/DoctorManagement';
import CourseManagement from './pages/admin/CourseManagement';
import LectureManagement from './pages/admin/LectureManagement';
import Statistics from './pages/admin/Statistics';
import DoctorDashboard from './pages/doctor/Dashboard';
import CourseDetails from './pages/doctor/CourseDetails';
import AttendanceStatistics from './pages/doctor/AttendanceStatistics';
import AttendanceScreen from './pages/attendance/AttendanceScreen';
import Navbar from './components/Navbar';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const user = authService.getCurrentUser();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [userRole, setUserRole] = useState(authService.getUserRole());

  useEffect(() => {
    const checkAuth = () => {
      setIsAuthenticated(authService.isAuthenticated());
      setUserRole(authService.getUserRole());
    };
    
    checkAuth();
    // Listen for storage changes (for multi-tab support)
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  return (
    <Router>
      <div className="App">
        {isAuthenticated && <Navbar />}
        <div className="container-fluid mt-4">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                isAuthenticated ? 
                <Navigate to={`/${userRole}/dashboard`} replace /> : 
                <Login onLogin={() => {
                  setIsAuthenticated(true);
                  setUserRole(authService.getUserRole());
                }} />
              } 
            />
            
            {/* Admin Routes */}
            <Route 
              path="/admin/dashboard" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/students" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <StudentManagement />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/doctors" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <DoctorManagement />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/courses" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <CourseManagement />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/lectures" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <LectureManagement />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/statistics" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <Statistics />
                </ProtectedRoute>
              } 
            />
            
            {/* Doctor Routes */}
            <Route 
              path="/doctor/dashboard" 
              element={
                <ProtectedRoute allowedRoles={['doctor']}>
                  <DoctorDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/doctor/course/:courseId" 
              element={
                <ProtectedRoute allowedRoles={['doctor']}>
                  <CourseDetails />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/doctor/attendance-stats" 
              element={
                <ProtectedRoute allowedRoles={['doctor']}>
                  <AttendanceStatistics />
                </ProtectedRoute>
              } 
            />
            
            {/* Attendance Screen (Public for classroom device) */}
            <Route path="/attendance/:crnId" element={<AttendanceScreen />} />
            
            {/* Default Routes */}
            <Route 
              path="/" 
              element={
                <Navigate to={isAuthenticated ? `/${userRole}/dashboard` : '/login'} replace />
              } 
            />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;