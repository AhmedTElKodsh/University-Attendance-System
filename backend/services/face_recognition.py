import face_recognition
import numpy as np
from typing import Optional, Tuple, List
from backend.config import settings
from backend.database import FaceProfile, Student


class FaceRecognitionService:
    """Service for face embedding generation and matching"""
    
    def __init__(self, confidence_threshold: Optional[float] = None):
        self.confidence_threshold = confidence_threshold or settings.FACE_CONFIDENCE_THRESHOLD
    
    def extract_embedding(self, image) -> Optional[bytes]:
        """
        Extract face embedding from an image.
        Args:
            image: numpy array (BGR from OpenCV) or file path
        Returns:
            Face embedding as bytes, or None if no face detected
        """
        # Convert BGR to RGB if needed (OpenCV uses BGR)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = image[:, :, ::-1]  # BGR to RGB
        else:
            image_rgb = image
        
        # Get face encodings
        encodings = face_recognition.face_encodings(image_rgb)
        
        if not encodings:
            return None
        
        # Use the first face found
        embedding = encodings[0]
        
        # Validate embedding shape (should be 128-dimensional)
        if embedding.shape != (128,):
            return None
        
        return embedding.tobytes()
    
    def compare_embeddings(self, known_embedding_bytes: bytes, 
                          unknown_embedding_bytes: bytes) -> Tuple[bool, float]:
        """
        Compare two face embeddings.
        Returns: (is_match, confidence_score)
        """
        # Convert bytes back to numpy arrays
        known_embedding = np.frombuffer(known_embedding_bytes, dtype=np.float64)
        unknown_embedding = np.frombuffer(unknown_embedding_bytes, dtype=np.float64)
        
        # Validate embedding shapes
        if known_embedding.shape != (128,) or unknown_embedding.shape != (128,):
            return False, 0.0
        
        # Calculate face distance (0 = perfect match)
        distance = face_recognition.face_distance([known_embedding], unknown_embedding)[0]
        
        # Convert distance to confidence (1 - distance)
        confidence = 1.0 - distance
        
        return confidence >= self.confidence_threshold, confidence
    
    def recognize_face(self, image, face_profiles: List[FaceProfile]) -> Tuple[Optional[int], float]:
        """
        Recognize a face in an image against a list of face profiles.
        Returns: (student_id, confidence) or (None, 0.0) if no match
        """
        # Extract embedding from input image
        unknown_embedding_bytes = self.extract_embedding(image)
        if not unknown_embedding_bytes:
            return None, 0.0
        
        best_match_id = None
        best_confidence = 0.0
        
        for profile in face_profiles:
            is_match, confidence = self.compare_embeddings(
                profile.face_embedding, unknown_embedding_bytes
            )
            
            if is_match and confidence > best_confidence:
                best_confidence = confidence
                best_match_id = profile.student_id
        
        return best_match_id, best_confidence
    
    def register_face(self, image, student_id: int) -> Tuple[bool, Optional[bytes], str]:
        """
        Register a face for a student.
        Returns: (success, embedding_bytes, message)
        """
        embedding_bytes = self.extract_embedding(image)
        
        if not embedding_bytes:
            return False, None, "No face detected in the image"
        
        return True, embedding_bytes, "Face registered successfully"