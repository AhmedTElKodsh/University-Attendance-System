import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import Login from '../pages/Login';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Mock the authService
jest.mock('../services/api', () => ({
  authService: {
    login: jest.fn(),
    isAuthenticated: jest.fn(() => false),
    getUserRole: jest.fn(() => null),
  },
}));

describe('Login Component', () => {
  test('renders login form', () => {
    render(
      <BrowserRouter>
        <Login onLogin={jest.fn()} />
      </BrowserRouter>
    );
    
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('shows error on failed login', async () => {
    const mockOnLogin = jest.fn();
    mockedAxios.post.mockRejectedValueOnce({
      response: {
        data: { detail: 'Incorrect email or password' }
      }
    });
    
    render(
      <BrowserRouter>
        <Login onLogin={mockOnLogin} />
      </BrowserRouter>
    );
    
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/failed|incorrect/i);
    });
  });

  test('calls onLogin on successful login', async () => {
    const mockOnLogin = jest.fn();
    mockedAxios.post.mockResolvedValueOnce({
      data: { access_token: 'fake-token' }
    });
    
    render(
      <BrowserRouter>
        <Login onLogin={mockOnLogin} />
      </BrowserRouter>
    );
    
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalled();
    });
  });
});