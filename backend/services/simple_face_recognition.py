"""
Simplified face recognition using perceptual hashing
- Fast installation (no dlib dependency)
- Medium accuracy (~80% in controlled environment)
- Works on all platforms
- Good enough for supervised classroom attendance
"""
import imagehash
from PIL import Image
import numpy as np
from typing import Optional, Tuple, List
from backend.config import settings
from backend.database import FaceProfile


class SimpleFaceRecognitionService:
    """
    Simplified face recognition using perceptual hashing.
    Trade-off: Lower accuracy (80% vs 95%) but MUCH simpler deployment.
    """
    
    def __init__(self, similarity_threshold: int = 10):
        """
        Args:
            similarity_threshold: Max hamming distance for match (lower = stricter)
                                 10 = good balance for classroom environment
        """
        self.similarity_threshold = similarity_threshold
    
    def extract_hash(self, image) -> Optional[str]:
        """
        Extract perceptual hash from an image.
        Args:
            image: numpy array (BGR from OpenCV)
        Returns:
            Hash as hex string, or None if error
        """
        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = image[:, :, ::-1]  # BGR to RGB
            else:
                image_rgb = image
            
            # Convert to PIL Image
            pil_img = Image.fromarray(image_rgb)
            
            # Generate perceptual hash (robust to minor changes)
            hash_value = imagehash.phash(pil_img, hash_size=8)
            
            return str(hash_value)
        except Exception as e:
            print(f"Error extracting hash: {e}")
            return None
    
    def compare_hashes(self, hash1: str, hash2: str) -> Tuple[bool, int]:
        """
        Compare two perceptual hashes.
        Returns: (is_match, hamming_distance)
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            
            # Calculate hamming distance (0 = identical)
            distance = h1 - h2
            
            is_match = distance <= self.similarity_threshold
            
            return is_match, distance
        except Exception as e:
            print(f"Error comparing hashes: {e}")
            return False, 999
    
    def recognize_face(self, image, face_profiles: List[FaceProfile]) -> Tuple[Optional[int], float]:
        """
        Recognize a face in an image against a list of face profiles.
        Returns: (student_id, confidence) or (None, 0.0) if no match
        
        Note: face_profiles should have face_embedding as string hash (not bytes)
        """
        # Extract hash from input image
        unknown_hash = self.extract_hash(image)
        if not unknown_hash:
            return None, 0.0
        
        best_match_id = None
        best_distance = 999
        
        for profile in face_profiles:
            # Convert bytes to string if needed
            if isinstance(profile.face_embedding, bytes):
                stored_hash = profile.face_embedding.decode('utf-8')
            else:
                stored_hash = profile.face_embedding
            
            is_match, distance = self.compare_hashes(stored_hash, unknown_hash)
            
            if is_match and distance < best_distance:
                best_distance = distance
                best_match_id = profile.student_id
        
        # Convert distance to confidence (0-1 scale)
        # Lower distance = higher confidence
        if best_match_id:
            confidence = max(0.0, 1.0 - (best_distance / 64.0))  # 64 = max possible distance
        else:
            confidence = 0.0
        
        return best_match_id, confidence
    
    def register_face(self, image, student_id: int) -> Tuple[bool, Optional[bytes], str]:
        """
        Register a face for a student.
        Returns: (success, hash_bytes, message)
        """
        hash_str = self.extract_hash(image)
        
        if not hash_str:
            return False, None, "Could not extract face hash from image"
        
        # Convert to bytes for storage
        hash_bytes = hash_str.encode('utf-8')
        
        return True, hash_bytes, "Face registered successfully"


# Factory function to choose between simple and advanced
def get_face_recognition_service():
    """
    Returns appropriate face recognition service based on availability.
    Falls back to simple service if advanced libraries not available.
    """
    use_simple = settings.USE_SIMPLE_FACE_RECOGNITION if hasattr(settings, 'USE_SIMPLE_FACE_RECOGNITION') else False
    
    if use_simple:
        print("ℹ️  Using simplified face recognition (imagehash)")
        return SimpleFaceRecognitionService()
    
    try:
        from backend.services.face_recognition import FaceRecognitionService
        print("ℹ️  Using advanced face recognition (dlib)")
        return FaceRecognitionService()
    except ImportError as e:
        print(f"⚠️  Advanced face recognition not available: {e}")
        print("ℹ️  Falling back to simplified face recognition")
        return SimpleFaceRecognitionService()
