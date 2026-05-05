import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AttendanceScreen from '../pages/attendance/AttendanceScreen';
import { attendanceService } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  attendanceService: {
    getAttendanceScreen: jest.fn(),
    recordAttendance: jest.fn(),
    registerFace: jest.fn()
  },
  authService: {
    getUserRole: jest.fn(() => 'doctor'),
    isAuthenticated: jest.fn(() => true)
  }
}));

// Mock getUserMedia
global.navigator.mediaDevices = {
  getUserMedia: jest.fn(() => Promise.resolve({
    getTracks: () => [{ stop: jest.fn() }]
  }))
};

describe('AttendanceScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders attendance screen heading', () => {
    attendanceService.getAttendanceScreen.mockResolvedValue({
      data: { crn_id: 1, course_name: 'CS101', lecture_id: 1 }
    });

    render(
      <BrowserRouter>
        <AttendanceScreen />
      </BrowserRouter>
    );

    expect(screen.getByText(/Attendance Screen/i)).toBeInTheDocument();
  });

  test('displays camera feed when available', async () => {
    attendanceService.getAttendanceScreen.mockResolvedValue({
      data: { crn_id: 1, course_name: 'CS101', lecture_id: 1 }
    });

    render(
      <BrowserRouter>
        <AttendanceScreen />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Camera Feed/i)).toBeInTheDocument();
    });
  });

  test('handles attendance recording', async () => {
    attendanceService.getAttendanceScreen.mockResolvedValue({
      data: { crn_id: 1, course_name: 'CS101', lecture_id: 1 }
    });
    attendanceService.recordAttendance.mockResolvedValue({
      data: { status: 'present' }
    });

    render(
      <BrowserRouter>
        <AttendanceScreen />
      </BrowserRouter>
    );

    const recordButton = screen.getByText(/Record Attendance/i);
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(attendanceService.recordAttendance).toHaveBeenCalled();
    });
  });
});