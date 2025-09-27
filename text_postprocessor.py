"""
Text postprocessing module for Vietnamese Speech-to-Text
Handles text cleaning, normalization, and punctuation
"""
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextPostprocessor:
    """Text postprocessing class for Vietnamese speech-to-text"""
    
    def __init__(self):
        # Vietnamese punctuation patterns
        self.punctuation_patterns = {
            r'\s+([.!?])': r'\1',  # Remove spaces before punctuation
            r'([.!?])\s*([a-z])': r'\1 \2',  # Add space after punctuation
            r'([.!?])\s*([A-Z])': r'\1 \2',  # Add space after punctuation for capital letters
        }
        
        # Common Vietnamese abbreviations and their expansions
        self.abbreviations = {
            'và': 'và',
            'của': 'của',
            'được': 'được',
            'không': 'không',
            'này': 'này',
            'đó': 'đó',
            'với': 'với',
            'từ': 'từ',
            'đến': 'đến',
            'trong': 'trong',
            'ngoài': 'ngoài',
            'trên': 'trên',
            'dưới': 'dưới',
            'giữa': 'giữa',
            'sau': 'sau',
            'trước': 'trước',
            'bên': 'bên',
            'cạnh': 'cạnh',
            'gần': 'gần',
            'xa': 'xa'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Cleaned text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove leading/trailing whitespace
            text = text.strip()
            
            # Remove special characters that might be artifacts
            text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
            
            # Normalize Vietnamese characters
            text = self._normalize_vietnamese_chars(text)
            
            logger.info("Text cleaned successfully")
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text
    
    def _normalize_vietnamese_chars(self, text: str) -> str:
        """
        Normalize Vietnamese characters
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Common character normalizations
        char_mappings = {
            'à': 'à', 'á': 'á', 'ả': 'ả', 'ã': 'ã', 'ạ': 'ạ',
            'ă': 'ă', 'ằ': 'ằ', 'ắ': 'ắ', 'ẳ': 'ẳ', 'ẵ': 'ẵ', 'ặ': 'ặ',
            'â': 'â', 'ầ': 'ầ', 'ấ': 'ấ', 'ẩ': 'ẩ', 'ẫ': 'ẫ', 'ậ': 'ậ',
            'è': 'è', 'é': 'é', 'ẻ': 'ẻ', 'ẽ': 'ẽ', 'ẹ': 'ẹ',
            'ê': 'ê', 'ề': 'ề', 'ế': 'ế', 'ể': 'ể', 'ễ': 'ễ', 'ệ': 'ệ',
            'ì': 'ì', 'í': 'í', 'ỉ': 'ỉ', 'ĩ': 'ĩ', 'ị': 'ị',
            'ò': 'ò', 'ó': 'ó', 'ỏ': 'ỏ', 'õ': 'õ', 'ọ': 'ọ',
            'ô': 'ô', 'ồ': 'ồ', 'ố': 'ố', 'ổ': 'ổ', 'ỗ': 'ỗ', 'ộ': 'ộ',
            'ơ': 'ơ', 'ờ': 'ờ', 'ớ': 'ớ', 'ở': 'ở', 'ỡ': 'ỡ', 'ợ': 'ợ',
            'ù': 'ù', 'ú': 'ú', 'ủ': 'ủ', 'ũ': 'ũ', 'ụ': 'ụ',
            'ư': 'ư', 'ừ': 'ừ', 'ứ': 'ứ', 'ử': 'ử', 'ữ': 'ữ', 'ự': 'ự',
            'ỳ': 'ỳ', 'ý': 'ý', 'ỷ': 'ỷ', 'ỹ': 'ỹ', 'ỵ': 'ỵ',
            'đ': 'đ'
        }
        
        # Apply character mappings
        for old_char, new_char in char_mappings.items():
            text = text.replace(old_char, new_char)
        
        return text
    
    def add_punctuation(self, text: str) -> str:
        """
        Add basic punctuation to text
        
        Args:
            text: Input text
            
        Returns:
            Text with added punctuation
        """
        try:
            # Add period at the end if no punctuation
            if text and not text[-1] in '.!?':
                text += '.'
            
            # Apply punctuation patterns
            for pattern, replacement in self.punctuation_patterns.items():
                text = re.sub(pattern, replacement, text)
            
            logger.info("Punctuation added successfully")
            return text
            
        except Exception as e:
            logger.error(f"Error adding punctuation: {e}")
            return text
    
    def capitalize_sentences(self, text: str) -> str:
        """
        Capitalize first letter of sentences
        
        Args:
            text: Input text
            
        Returns:
            Text with capitalized sentences
        """
        try:
            # Split by sentence endings
            sentences = re.split(r'([.!?]+)', text)
            
            result = []
            for i, part in enumerate(sentences):
                if i % 2 == 0:  # Text part
                    if part.strip():
                        # Capitalize first letter
                        part = part.strip()
                        if part:
                            part = part[0].upper() + part[1:]
                        result.append(part)
                else:  # Punctuation part
                    result.append(part)
            
            text = ''.join(result)
            logger.info("Sentences capitalized successfully")
            return text
            
        except Exception as e:
            logger.error(f"Error capitalizing sentences: {e}")
            return text
    
    def postprocess(self, text: str, add_punctuation: bool = True, capitalize: bool = True) -> str:
        """
        Complete text postprocessing pipeline
        
        Args:
            text: Raw transcribed text
            add_punctuation: Whether to add punctuation
            capitalize: Whether to capitalize sentences
            
        Returns:
            Postprocessed text
        """
        try:
            # Clean text
            text = self.clean_text(text)
            
            # Add punctuation if requested
            if add_punctuation:
                text = self.add_punctuation(text)
            
            # Capitalize sentences if requested
            if capitalize:
                text = self.capitalize_sentences(text)
            
            logger.info("Text postprocessing completed")
            return text
            
        except Exception as e:
            logger.error(f"Error in text postprocessing: {e}")
            return text
    
    def format_output(self, text: str, format_type: str = "plain") -> str:
        """
        Format output text for different use cases
        
        Args:
            text: Postprocessed text
            format_type: Output format ("plain", "json", "formatted")
            
        Returns:
            Formatted text
        """
        try:
            if format_type == "plain":
                return text
            elif format_type == "json":
                import json
                return json.dumps({"transcription": text}, ensure_ascii=False, indent=2)
            elif format_type == "formatted":
                # Add line breaks for better readability
                sentences = re.split(r'([.!?]+)', text)
                formatted = []
                for i, part in enumerate(sentences):
                    if i % 2 == 0 and part.strip():  # Text part
                        formatted.append(part.strip())
                    elif i % 2 == 1:  # Punctuation part
                        formatted.append(part)
                return '\n'.join(formatted)
            else:
                return text
                
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return text
