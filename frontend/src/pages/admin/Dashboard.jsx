import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await adminService.getStats();
      setStats(response.data);
    } catch (err) {
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" />
      </Container>
    );
  }

  return (
    <Container>
      <h2 className="mb-4">Admin Dashboard</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      
      {stats && (
        <>
          <Row className="mb-4">
            <Col md={3}>
              <Card bg="primary" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Students</Card.Title>
                  <Card.Text as="h3">{stats.total_students}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card bg="success" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Doctors</Card.Title>
                  <Card.Text as="h3">{stats.total_doctors}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card bg="info" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Courses</Card.Title>
                  <Card.Text as="h3">{stats.total_courses}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card bg="warning" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Lectures</Card.Title>
                  <Card.Text as="h3">{stats.total_lectures}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>Quick Actions</Card.Header>
                <Card.Body>
                  <div className="d-grid gap-2">
                    <Button as={Link} to="/admin/students" variant="outline-primary">
                      Manage Students
                    </Button>
                    <Button as={Link} to="/admin/doctors" variant="outline-success">
                      Manage Doctors
                    </Button>
                    <Button as={Link} to="/admin/courses" variant="outline-info">
                      Manage Courses
                    </Button>
                    <Button as={Link} to="/admin/lectures" variant="outline-warning">
                      Manage Lectures
                    </Button>
                    <Button as={Link} to="/admin/statistics" variant="secondary">
                      View Detailed Statistics
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>System Overview</Card.Header>
                <Card.Body>
                  <p><strong>Total Attendance Records:</strong> {stats.total_attendance_records}</p>
                  <p className="text-muted">Use the navigation bar to manage different aspects of the system.</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </Container>
  );
};

export default Dashboard;