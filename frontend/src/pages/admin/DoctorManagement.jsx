import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Table, Alert, Spinner, Modal } from 'react-bootstrap';
import { adminService } from '../../services/api';

const DoctorManagement = () => {
  const [doctors, setDoctors] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  
  const [formData, setFormData] = useState({
    user_id: '',
    staff_id: '',
    full_name: '',
    email: '',
    phone: '',
    faculty: '',
    department: '',
    academic_title: ''
  });

  useEffect(() => {
    fetchDoctors();
    fetchUsers();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await adminService.getDoctors();
      setDoctors(response.data);
    } catch (err) {
      setError('Failed to load doctors');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    // In a real app, you'd have an endpoint to get users with role='doctor'
    // For MVP, we'll skip this or create a simple mock
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
      if (editingDoctor) {
        await adminService.updateDoctor(editingDoctor.id, formData);
      } else {
        await adminService.createDoctor(formData);
      }
      setShowModal(false);
      setEditingDoctor(null);
      resetForm();
      fetchDoctors();
    } catch (err) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (doctor) => {
    setEditingDoctor(doctor);
    setFormData({
      user_id: doctor.user_id,
      staff_id: doctor.staff_id,
      full_name: doctor.full_name,
      email: doctor.email,
      phone: doctor.phone || '',
      faculty: doctor.faculty,
      department: doctor.department,
      academic_title: doctor.academic_title
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      user_id: '',
      staff_id: '',
      full_name: '',
      email: '',
      phone: '',
      faculty: '',
      department: '',
      academic_title: ''
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
        <h2>Doctor Management</h2>
        <Button variant="primary" onClick={() => { resetForm(); setEditingDoctor(null); setShowModal(true); }}>
          Add New Doctor
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Staff ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Faculty</th>
                <th>Title</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {doctors.map(doctor => (
                <tr key={doctor.id}>
                  <td>{doctor.staff_id}</td>
                  <td>{doctor.full_name}</td>
                  <td>{doctor.email}</td>
                  <td>{doctor.faculty}</td>
                  <td>{doctor.academic_title}</td>
                  <td>
                    <Button variant="info" size="sm" className="me-2" onClick={() => handleEdit(doctor)}>
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
          <Modal.Title>{editingDoctor ? 'Edit Doctor' : 'Add New Doctor'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>User ID</Form.Label>
              <Form.Control type="number" name="user_id" value={formData.user_id} onChange={handleInputChange} required disabled={editingDoctor} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Staff ID</Form.Label>
              <Form.Control type="text" name="staff_id" value={formData.staff_id} onChange={handleInputChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Full Name</Form.Label>
              <Form.Control type="text" name="full_name" value={formData.full_name} onChange={handleInputChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control type="email" name="email" value={formData.email} onChange={handleInputChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Phone</Form.Label>
              <Form.Control type="text" name="phone" value={formData.phone} onChange={handleInputChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Faculty</Form.Label>
              <Form.Control type="text" name="faculty" value={formData.faculty} onChange={handleInputChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Department</Form.Label>
              <Form.Control type="text" name="department" value={formData.department} onChange={handleInputChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Academic Title</Form.Label>
              <Form.Control type="text" name="academic_title" value={formData.academic_title} onChange={handleInputChange} required />
            </Form.Group>
            <div className="d-grid">
              <Button variant="primary" type="submit">{editingDoctor ? 'Update' : 'Create'}</Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default DoctorManagement;