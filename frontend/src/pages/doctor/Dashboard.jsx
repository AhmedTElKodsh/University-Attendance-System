import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Button, ListGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { doctorService } from '../../services/api';

const Dashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await doctorService.getAssignedCourses();
      setCourses(response.data || []);
    } catch (err) {
      setError('Failed to load assigned courses');
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
      <h2 className="mb-4">Doctor Dashboard</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Row>
        <Col md={8}>
          <Card>
            <Card.Header>My Assigned Courses</Card.Header>
            <Card.Body>
              {courses.length === 0 ? (
                <p className="text-muted">No courses assigned yet.</p>
              ) : (
                <ListGroup variant="flush">
                  {courses.map(course => (
                    <ListGroup.Item key={course.crn_id}>
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h5>{course.course_name}</h5>
                          <p className="mb-1 text-muted">
                            {course.course_code} | CRN: {course.crn}
                          </p>
                          <small>
                            {course.day_of_week} {course.start_time}-{course.end_time} | 
                            {course.location} - {course.room}
                          </small>
                        </div>
                        <Button 
                          as={Link} 
                          to={`/doctor/course/${course.course_id}`}
                          variant="primary"
                          size="sm"
                        >
                          View Details
                        </Button>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button as={Link} to="/doctor/attendance-stats" variant="info">
                  View Attendance Statistics
                </Button>
                <Button variant="secondary" disabled>
                  Manage Lectures (Coming Soon)
                </Button>
              </div>
            </Card.Body>
          </Card>
          
          <Card className="mt-3">
            <Card.Header>Summary</Card.Header>
            <Card.Body>
              <p><strong>Total Assigned Courses:</strong> {courses.length}</p>
              <p className="text-muted">Click on a course to view lecture details and manage attendance.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;