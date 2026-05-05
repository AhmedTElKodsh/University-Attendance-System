import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Table } from 'react-bootstrap';
import { adminService } from '../../services/api';

const Statistics = () => {
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
      <h2 className="mb-4">System Statistics</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      
      {stats && (
        <>
          <Row className="mb-4">
            <Col md={4}>
              <Card bg="primary" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Total Students</Card.Title>
                  <Card.Text as="h3">{stats.total_students}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card bg="success" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Total Doctors</Card.Title>
                  <Card.Text as="h3">{stats.total_doctors}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card bg="info" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Total Courses</Card.Title>
                  <Card.Text as="h3">{stats.total_courses}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mb-4">
            <Col md={6}>
              <Card bg="warning" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Total Lectures</Card.Title>
                  <Card.Text as="h3">{stats.total_lectures}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card bg="danger" text="white" className="mb-2">
                <Card.Body>
                  <Card.Title>Total Attendance Records</Card.Title>
                  <Card.Text as="h3">{stats.total_attendance_records}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Card>
            <Card.Header>System Overview</Card.Header>
            <Card.Body>
              <p>The system currently has <strong>{stats.total_students} students</strong> enrolled across <strong>{stats.total_courses} courses</strong>, taught by <strong>{stats.total_doctors} doctors</strong>.</p>
              <p>A total of <strong>{stats.total_lectures} lectures</strong> have been scheduled, with <strong>{stats.total_attendance_records} attendance records</strong> recorded.</p>
              <p className="text-muted">Use the navigation bar to manage different aspects of the system.</p>
            </Card.Body>
          </Card>
        </>
      )}
    </Container>
  );
};

export default Statistics;