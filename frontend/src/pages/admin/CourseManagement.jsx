import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Table, Alert, Spinner, Modal } from 'react-bootstrap';
import { adminService } from '../../services/api';

const CourseManagement = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  
  const [formData, setFormData] = useState({
    course_name: '',
    course_code: '',
    description: '',
    faculty: '',
    department: '',
    academic_year: '',
    semester: ''
  });

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await adminService.getCourses();
      setCourses(response.data);
    } catch (err) {
      setError('Failed to load courses');
    } finally {
      setLoading(false);
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
      if (editingCourse) {
        await adminService.updateCourse(editingCourse.id, formData);
      } else {
        await adminService.createCourse(formData);
      }
      setShowModal(false);
      setEditingCourse(null);
      resetForm();
      fetchCourses();
    } catch (err) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (course) => {
    setEditingCourse(course);
    setFormData({
      course_name: course.course_name,
      course_code: course.course_code,
      description: course.description || '',
      faculty: course.faculty,
      department: course.department,
      academic_year: course.academic_year,
      semester: course.semester
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      course_name: '',
      course_code: '',
      description: '',
      faculty: '',
      department: '',
      academic_year: '',
      semester: ''
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
        <h2>Course Management</h2>
        <Button variant="primary" onClick={() => { resetForm(); setEditingCourse(null); setShowModal(true); }}>
          Add New Course
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Course Code</th>
                <th>Course Name</th>
                <th>Faculty</th>
                <th>Department</th>
                <th>Year</th>
                <th>Semester</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map(course => (
                <tr key={course.id}>
                  <td>{course.course_code}</td>
                  <td>{course.course_name}</td>
                  <td>{course.faculty}</td>
                  <td>{course.department}</td>
                  <td>{course.academic_year}</td>
                  <td>{course.semester}</td>
                  <td>
                    <Button variant="info" size="sm" className="me-2" onClick={() => handleEdit(course)}>
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{editingCourse ? 'Edit Course' : 'Add New Course'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Course Code</Form.Label>
              <Form.Control
                type="text"
                name="course_code"
                value={formData.course_code}
                onChange={handleInputChange}
                required
                disabled={editingCourse}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Course Name</Form.Label>
              <Form.Control
                type="text"
                name="course_name"
                value={formData.course_name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Faculty</Form.Label>
              <Form.Control
                type="text"
                name="faculty"
                value={formData.faculty}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Department</Form.Label>
              <Form.Control
                type="text"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Academic Year</Form.Label>
              <Form.Control
                type="text"
                name="academic_year"
                value={formData.academic_year}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Semester</Form.Label>
              <Form.Control
                type="text"
                name="semester"
                value={formData.semester}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <div className="d-grid">
              <Button variant="primary" type="submit">
                {editingCourse ? 'Update' : 'Create'}
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default CourseManagement;