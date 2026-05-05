import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Alert, Spinner, Modal } from 'react-bootstrap';
import { adminService } from '../../services/api';

const StudentManagement = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    student_id: '',
    full_name: '',
    email: '',
    phone: '',
    faculty: '',
    department: '',
    academic_level: '',
    program: ''
  });

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await adminService.getStudents();
      setStudents(response.data);
    } catch (err) {
      setError('Failed to load students');
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
      if (editingStudent) {
        await adminService.updateStudent(editingStudent.id, formData);
      } else {
        await adminService.createStudent(formData);
      }
      setShowModal(false);
      setEditingStudent(null);
      resetForm();
      fetchStudents();
    } catch (err) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (student) => {
    setEditingStudent(student);
    setFormData({
      student_id: student.student_id,
      full_name: student.full_name,
      email: student.email || '',
      phone: student.phone || '',
      faculty: student.faculty,
      department: student.department,
      academic_level: student.academic_level,
      program: student.program
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this student?')) {
      try {
        await adminService.deleteStudent(id);
        fetchStudents();
      } catch (err) {
        setError('Failed to delete student');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      student_id: '',
      full_name: '',
      email: '',
      phone: '',
      faculty: '',
      department: '',
      academic_level: '',
      program: ''
    });
  };

  const handleShowModal = () => {
    resetForm();
    setEditingStudent(null);
    setShowModal(true);
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
        <h2>Student Management</h2>
        <Button variant="primary" onClick={handleShowModal}>
          Add New Student
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Faculty</th>
                <th>Program</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map(student => (
                <tr key={student.id}>
                  <td>{student.student_id}</td>
                  <td>{student.full_name}</td>
                  <td>{student.email || '-'}</td>
                  <td>{student.faculty}</td>
                  <td>{student.program}</td>
                  <td>
                    <Button 
                      variant="info" 
                      size="sm" 
                      className="me-2"
                      onClick={() => handleEdit(student)}
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="danger" 
                      size="sm"
                      onClick={() => handleDelete(student.id)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* Add/Edit Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingStudent ? 'Edit Student' : 'Add New Student'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Student ID</Form.Label>
              <Form.Control
                type="text"
                name="student_id"
                value={formData.student_id}
                onChange={handleInputChange}
                required
                disabled={editingStudent}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Full Name</Form.Label>
              <Form.Control
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Phone</Form.Label>
              <Form.Control
                type="text"
                name="phone"
                value={formData.phone}
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
              <Form.Label>Academic Level</Form.Label>
              <Form.Control
                type="text"
                name="academic_level"
                value={formData.academic_level}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Program</Form.Label>
              <Form.Control
                type="text"
                name="program"
                value={formData.program}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            
            <div className="d-grid">
              <Button variant="primary" type="submit">
                {editingStudent ? 'Update' : 'Create'}
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default StudentManagement;