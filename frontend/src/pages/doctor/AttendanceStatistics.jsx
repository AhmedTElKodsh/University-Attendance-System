import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Form, Table } from 'react-bootstrap';
import { doctorService } from '../../services/api';

const AttendanceStatistics = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingStats, setLoadingStats] = useState(false);
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
      setError('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async (courseId) => {
    try {
      setLoadingStats(true);
      setError('');
      const response = await doctorService.getAttendanceStats(courseId);
      setStats(response.data || []);
    } catch (err) {
      setError('Failed to load attendance statistics');
    } finally {
      setLoadingStats(false);
    }
  };

  const handleCourseChange = (e) => {
    const courseId = e.target.value;
    setSelectedCourse(courseId);
    if (courseId) {
      fetchStats(courseId);
    } else {
      setStats([]);
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
      <h2 className="mb-4">Attendance Statistics</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card className="mb-4">
        <Card.Body>
          <Form.Group>
            <Form.Label>Select Course</Form.Label>
            <Form.Select value={selectedCourse} onChange={handleCourseChange}>
              <option value="">Choose a course...</option>
              {courses.map(course => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_name} ({course.course_code})
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Card.Body>
      </Card>

      {loadingStats ? (
        <div className="text-center">
          <Spinner animation="border" />
        </div>
      ) : (
        <>
          {stats.length > 0 ? (
            <>
              <Row className="mb-4">
                <Col md={4}>
                  <Card bg="success" text="white">
                    <Card.Body>
                      <Card.Title>Total Lectures</Card.Title>
                      <Card.Text as="h3">{stats.length}</Card.Text>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card bg="info" text="white">
                    <Card.Body>
                      <Card.Title>Average Attendance</Card.Title>
                      <Card.Text as="h3">
                        {stats.length > 0 
                          ? Math.round(
                              stats.reduce((acc, s) => acc + (s.present_count / s.total_enrolled * 100), 0) / stats.length
                            ) + '%'
                          : '0%'
                        }
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card bg="warning" text="white">
                    <Card.Body>
                      <Card.Title>Total Students</Card.Title>
                      <Card.Text as="h3">
                        {stats.length > 0 ? stats[0].total_enrolled : 0}
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <Card>
                <Card.Header>Lecture-wise Attendance</Card.Header>
                <Card.Body>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Course</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>Total Enrolled</th>
                        <th>Attendance Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.map(stat => {
                        const rate = stat.total_enrolled > 0 
                          ? Math.round(stat.present_count / stat.total_enrolled * 100) 
                          : 0;
                        return (
                          <tr key={stat.lecture_id}>
                            <td>{new Date(stat.date).toLocaleDateString()}</td>
                            <td>{stat.course_name}</td>
                            <td><span className="text-success">{stat.present_count}</span></td>
                            <td><span className="text-danger">{stat.absent_count}</span></td>
                            <td>{stat.total_enrolled}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                <div className="me-2" style={{width: '60px'}}>{rate}%</div>
                                <div className="progress flex-grow-1" style={{height: '20px'}}>
                                  <div 
                                    className={`progress-bar ${rate >= 75 ? 'bg-success' : rate >= 50 ? 'bg-warning' : 'bg-danger'}`}
                                    role="progressbar" 
                                    style={{width: `${rate}%`}}
                                  >
                                    {rate}%
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </>
          ) : selectedCourse ? (
            <Alert variant="info">No attendance data found for this course.</Alert>
          ) : (
            <Alert variant="info">Please select a course to view attendance statistics.</Alert>
          )}
        </>
      )}
    </Container>
  );
};

export default AttendanceStatistics;