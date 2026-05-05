import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Alert, Spinner, ProgressBar } from 'react-bootstrap';
import { attendanceService } from '../../services/api';

const AttendanceScreen = () => {
  const { crnId } = useParams();
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  const [screenData, setScreenData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cameraActive, setCameraActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [result, setResult] = useState(null);
  const [stream, setStream] = useState(null);

  useEffect(() => {
    fetchScreenData();
    return () => {
      stopCamera();
    };
  }, [crnId]);

  const fetchScreenData = async () => {
    try {
      setLoading(true);
      const response = await attendanceService.getAttendanceScreen(crnId);
      setScreenData(response.data);
    } catch (err) {
      setError('Failed to load attendance screen data');
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setCameraActive(true);
    } catch (err) {
      setError('Failed to access camera. Please allow camera permission.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  const captureAndRecord = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    setRecording(true);
    setError('');
    setResult(null);
    
    try {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      // Convert to blob
      canvas.toBlob(async (blob) => {
        if (!blob) {
          setError('Failed to capture image');
          setRecording(false);
          return;
        }
        
        try {
          const response = await attendanceService.recordAttendance(screenData.lecture_id, blob);
          setResult({
            success: true,
            message: 'Attendance recorded successfully!',
            data: response.data
          });
          stopCamera();
        } catch (err) {
          setResult({
            success: false,
            message: err.response?.data?.detail || 'Failed to record attendance'
          });
        } finally {
          setRecording(false);
        }
      }, 'image/jpeg');
    } catch (err) {
      setError('Failed to capture image');
      setRecording(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" />
      </Container>
    );
  }

  if (!screenData) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">Failed to load attendance screen</Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      <Row className="justify-content-center">
        <Col md={8}>
          <Card>
            <Card.Header as="h4" className="text-center bg-primary text-white">
              Attendance Screen
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              
              <div className="mb-3">
                <h5>{screenData.course_name}</h5>
                <p className="mb-1">
                  <strong>CRN:</strong> {screenData.crn} | 
                  <strong>Room:</strong> {screenData.room}
                </p>
                <p className="text-muted">{screenData.location}</p>
              </div>

              {!screenData.attendance_open ? (
                <Alert variant="warning">
                  <Alert.Heading>Attendance is Closed</Alert.Heading>
                  <p>The attendance window for this lecture is not currently open.</p>
                  {screenData.time_remaining && (
                    <p>Time remaining: {Math.floor(screenData.time_remaining / 60)} minutes</p>
                  )}
                </Alert>
              ) : (
                <>
                  <div className="text-center mb-3">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      style={{ width: '100%', maxWidth: '640px', borderRadius: '8px' }}
                    />
                    <canvas ref={canvasRef} style={{ display: 'none' }} />
                  </div>

                  {!cameraActive ? (
                    <div className="d-grid gap-2">
                      <Button variant="primary" size="lg" onClick={startCamera}>
                        Start Camera
                      </Button>
                    </div>
                  ) : (
                    <div className="d-grid gap-2">
                      <Button 
                        variant="success" 
                        size="lg" 
                        onClick={captureAndRecord}
                        disabled={recording}
                      >
                        {recording ? 'Recording...' : 'Mark Attendance'}
                      </Button>
                      <Button variant="secondary" onClick={stopCamera}>
                        Stop Camera
                      </Button>
                    </div>
                  )}
                </>
              )}

              {result && (
                <Alert variant={result.success ? 'success' : 'danger'} className="mt-3">
                  <Alert.Heading>{result.success ? 'Success!' : 'Error'}</Alert.Heading>
                  <p>{result.message}</p>
                  {result.data && (
                    <div>
                      <p><strong>Student:</strong> {result.data.student_name}</p>
                      <p><strong>Student ID:</strong> {result.data.student_id}</p>
                      <p><strong>Time:</strong> {new Date(result.data.attendance_time).toLocaleString()}</p>
                    </div>
                  )}
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AttendanceScreen;