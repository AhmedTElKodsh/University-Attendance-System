import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Table, Alert, Spinner, Modal } from 'react-bootstrap';
import { adminService } from '../../services/api';

const LectureManagement = () => {
  const [lectures, setLectures] = useState([]);
  const [courses, setCourses] = useState([]);
  const [crns, setCRNs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingLecture, setEditingLecture] = useState(null);
  
  const [formData, setFormData] = useState({
    course_id: '',
    crn_id: '',
    doctor_id: '',
    lecture_date: '',
    start_time: '',
    end_time: '',
    attendance_open_time: '',
    attendance_close_time: '',
    location: ''
  });

  useEffect(() => {
    fetchLectures();
    fetchCourses();
    fetchCRNs();
  }, []);

  const fetchLectures = async () => {
    try {
      setLoading(true);
      const response = await adminService.getLectures();
      setLectures(response.data);
    } catch (err) {
      setError('Failed to load lectures');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await adminService.getCourses();
      setCourses(response.data);
    } catch (err) {
      console.error('Failed to load courses');
    }
  };

  const fetchCRNs = async () => {
    try {
      const response = await adminService.getCRNs();
      setCRNs(response.data);
    } catch (err) {
      console.error('Failed to load CRNs');
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingLecture) {
        // Update logic would go here
        await adminService.updateLecture(editingLecture.id, formData);
      } else {
        await adminService.scheduleLecture(formData);
      }
      setShowModal(false);
      setEditingLecture(null);
      resetForm();
      fetchLectures();
    } catch (err) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const resetForm = () => {
    setFormData({
      course_id: '',
      crn_id: '',
      doctor_id: '',
      lecture_date: '',
      start_time: '',
      end_time: '',
      attendance_open_time: '',
      attendance_close_time: '',
      location: ''
    });
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
        <h2>Lecture Management</h2>
        <Button variant="primary" onClick={() => { resetForm(); setEditingLecture(null); setShowModal(true); }}>
          Schedule New Lecture
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Course</th>
                <th>Date</th>
                <th>Time</th>
                <th>Location</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {lectures.map(lecture => (
                <tr key={lecture.id}>
                  <td>{lecture.course_name || lecture.course_id}</td>
                  <td>{lecture.lecture_date}</td>
                  <td>{lecture.start_time} - {lecture.end_time}</td>
                  <td>{lecture.location}</td>
                  <td>{lecture.status}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{editingLecture ? 'Edit Lecture' : 'Schedule New Lecture'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Course</Form.Label>
              <Form.Select name="course_id" value={formData.course_id} onChange={handleInputChange} required>
                <option value="">Select Course</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.course_name}</option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>CRN</Form.Label>
              <Form.Select name="crn_id" value={formData.crn_id} onChange={handleInputChange} required>
                <option value="">Select CRN</option>
                {crns.map(crn => (
                  <option key={crn.id} value={crn.id}>{crn.crn} - {crn.location}</option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Lecture Date</Form.Label>
              <Form.Control type="date" name="lecture_date" value={formData.lecture_date} onChange={handleInputChange} required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Start Time</Form.Label>
              <Form.Control type="time" name="start_time" value={formData.start_time} onChange={handleInputChange} required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>End Time</Form.Label>
              <Form.Control type="time" name="end_time" value={formData.end_time} onChange={handleInputChange} required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Attendance Open Time</Form.Label>
              <Form.Control type="datetime-local" name="attendance_open_time" value={formData.attendance_open_time} onChange={handleInputChange} required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Attendance Close Time</Form.Label>
              <Form.Control type="datetime-local" name="attendance_close_time" value={formData.attendance_close_time} onChange={handleInputChange} required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Location</Form.Label>
              <Form.Control type="text" name="location" value={formData.location} onChange={handleInputChange} required />
            </Form.Group>
            
            <div className="d-grid">
              <Button variant="primary" type="submit">
                {editingLecture ? 'Update' : 'Schedule'}
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default LectureManagement;