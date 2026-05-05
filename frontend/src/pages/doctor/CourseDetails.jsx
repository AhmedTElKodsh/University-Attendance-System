import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Table, Spinner, Alert, Button, Badge } from 'react-bootstrap';
import { doctorService } from '../../services/api';

const CourseDetails = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [lectureDetails, setLectureDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [courseInfo, setCourseInfo] = useState(null);

  useEffect(() => {
    fetchLectureDetails();
  }, [courseId]);

  const fetchLectureDetails = async () => {
    try {
      setLoading(true);
      const response = await doctorService.getLectureDetails(courseId);
      if (response.data && response.data.lectures) {
        setLectureDetails(response.data.lectures);
        setCourseInfo({
          course_name: response.data.course_name,
          course_code: response.data.course_code
        });
      }
    } catch (err) {
      setError('Failed to load lecture details');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelLecture = async (lectureId) => {
    const reason = prompt('Enter cancellation reason:');
    if (!reason) return;
    
    try {
      await doctorService.cancelLecture(lectureId, reason);
      fetchLectureDetails();
    } catch (err) {
      setError('Failed to cancel lecture');
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
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>
          {courseInfo?.course_name || 'Course Details'}
          {courseInfo?.course_code && <small className="text-muted ms-2">{courseInfo.course_code}</small>}
        </h2>
        <Button variant="secondary" onClick={() => navigate('/doctor/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Header>Lectures</Card.Header>
        <Card.Body>
          {lectureDetails.length === 0 ? (
            <p className="text-muted">No lectures scheduled yet.</p>
          ) : (
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Attendance</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {lectureDetails.map(lecture => (
                  <tr key={lecture.id}>
                    <td>{new Date(lecture.lecture_date).toLocaleDateString()}</td>
                    <td>{lecture.start_time} - {lecture.end_time}</td>
                    <td>{lecture.location}</td>
                    <td>
                      <Badge bg={
                        lecture.status === 'active' ? 'success' :
                        lecture.status === 'scheduled' ? 'primary' :
                        lecture.status === 'cancelled' ? 'danger' : 'secondary'
                      }>
                        {lecture.status}
                      </Badge>
                    </td>
                    <td>
                      {lecture.attendance_count || 0} / {lecture.enrolled_count || 0}
                    </td>
                    <td>
                      {lecture.status !== 'cancelled' && (
                        <Button 
                          variant="warning" 
                          size="sm"
                          onClick={() => handleCancelLecture(lecture.id)}
                        >
                          Cancel
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default CourseDetails;