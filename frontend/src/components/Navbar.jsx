import React from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const CustomNavbar = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  const role = authService.getUserRole();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to={role ? `/${role}/dashboard` : '/login'}>
          Mustian Face
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {role === 'admin' && (
              <>
                <Nav.Link as={Link} to="/admin/dashboard">Dashboard</Nav.Link>
                <Nav.Link as={Link} to="/admin/students">Students</Nav.Link>
                <Nav.Link as={Link} to="/admin/doctors">Doctors</Nav.Link>
                <Nav.Link as={Link} to="/admin/courses">Courses</Nav.Link>
                <Nav.Link as={Link} to="/admin/lectures">Lectures</Nav.Link>
                <Nav.Link as={Link} to="/admin/statistics">Statistics</Nav.Link>
              </>
            )}
            {role === 'doctor' && (
              <>
                <Nav.Link as={Link} to="/doctor/dashboard">Dashboard</Nav.Link>
                <Nav.Link as={Link} to="/doctor/attendance-stats">Attendance Stats</Nav.Link>
              </>
            )}
          </Nav>
          {user && (
            <Nav className="ms-auto">
              <Navbar.Text className="me-3 text-light">
                {user.email} ({role})
              </Navbar.Text>
              <Button variant="outline-light" onClick={handleLogout}>
                Logout
              </Button>
            </Nav>
          )}
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;