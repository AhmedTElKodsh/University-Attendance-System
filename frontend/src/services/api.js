import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth services
export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 uses 'username'
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      const decoded = jwtDecode(response.data.access_token);
      localStorage.setItem('userRole', decoded.role);
      localStorage.setItem('userEmail', decoded.sub);
    }
    
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userEmail');
  },
  
  getCurrentUser: () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
      const decoded = jwtDecode(token);
      return {
        email: decoded.sub,
        role: decoded.role,
        token
      };
    } catch {
      return null;
    }
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  
  getUserRole: () => {
    return localStorage.getItem('userRole');
  }
};

// Admin services
export const adminService = {
  // Student management
  createStudent: (studentData) => api.post('/students/', studentData),
  updateStudent: (id, studentData) => api.put(`/students/${id}`, studentData),
  deleteStudent: (id) => api.delete(`/students/${id}`),
  getStudents: () => api.get('/students/'),
  
  // Doctor management
  createDoctor: (doctorData) => api.post('/admin/doctors', doctorData),
  updateDoctor: (id, doctorData) => api.put(`/admin/doctors/${id}`, doctorData),
  getDoctors: () => api.get('/admin/doctors'),
  
  // Course management
  createCourse: (courseData) => api.post('/courses/', courseData),
  updateCourse: (id, courseData) => api.put(`/courses/${id}`, courseData),
  getCourses: () => api.get('/courses/'),
  
  // CRN management
  createCRN: (crnData) => api.post('/courses/crns', crnData),
  getCRNs: () => api.get('/courses/crns'),
  
  // Lecture scheduling
  scheduleLecture: (lectureData) => api.post('/courses/lectures', lectureData),
  getLectures: () => api.get('/courses/lectures'),
  
  // Enrollment
  enrollStudent: (enrollmentData) => api.post('/admin/enrollments', enrollmentData),
  
  // Stats
  getStats: () => api.get('/admin/stats')
};

// Doctor services
export const doctorService = {
  getAssignedCourses: () => api.get('/doctor/courses'),
  getLectureDetails: (lectureId) => api.get(`/doctor/lectures/${lectureId}`),
  addAttendanceManual: (recordData) => api.post('/doctor/attendance/manual', recordData),
  removeAttendance: (recordId, reason) => api.put(`/doctor/attendance/${recordId}/remove`, null, {
    params: { reason }
  }),
  cancelLecture: (lectureId, reason) => api.put(`/doctor/lectures/${lectureId}/cancel`, null, {
    params: { reason }
  }),
  getAttendanceStats: (courseId) => api.get('/doctor/attendance/stats', {
    params: { course_id: courseId }
  })
};

// Attendance services
export const attendanceService = {
  getAttendanceScreen: (crnId) => api.get(`/attendance/screen/${crnId}`),
  startAttendanceSession: (lectureId) => api.put(`/attendance/session/${lectureId}/start`),
  recordAttendance: (lectureId, imageFile) => {
    const formData = new FormData();
    formData.append('lecture_id', lectureId);
    formData.append('image', imageFile);
    return api.post('/attendance/record', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  registerFace: (studentId, imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post(`/attendance/face/register/${studentId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export default api;