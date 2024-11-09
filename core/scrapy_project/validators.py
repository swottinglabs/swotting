from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, HttpUrl, UUID4, field_validator, Field
from decimal import Decimal
import pycountry

class CreatorBase(BaseModel):
    name: str
    url: Optional[HttpUrl] = None
    platform_id: Optional[str] = None
    description: Optional[str] = None
    platform_thumbnail_url: Optional[HttpUrl] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name must be less than 255 characters')
        return v.strip()

class LearningResourceBase(BaseModel):
    # Must have fields
    platform_course_id: str
    platform_id: str
    url: HttpUrl
    name: str
    description: str
    html_description: str
    languages: List[str]
    is_free: bool
    is_limited_free: bool
    is_active: bool

    # Important fields
    dollar_price: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    has_certificate: bool
    creators: List[CreatorBase] = []
    formats: List[str] = []
    tags: List[str] = []

    # Nice to have fields
    platform_last_update: Optional[datetime] = None
    platform_thumbnail_url: Optional[HttpUrl] = None
    duration_h: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    platform_reviews_count: Optional[int] = Field(default=0, ge=0)
    platform_reviews_rating: Optional[Decimal] = Field(
        None, 
        ge=1, 
        le=5, 
        decimal_places=2, 
        max_digits=3
    )
    enrollment_count: Optional[int] = Field(default=0, ge=0)
    level: Optional[str] = None
    short_description: Optional[str] = None

    @field_validator('name', 'platform_course_id', 'platform_id')
    @classmethod
    def validate_required_string_fields(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Field cannot be empty')
        if len(v) > 255:
            raise ValueError('Field must be less than 255 characters')
        return v.strip()

    @field_validator('description', 'html_description')
    @classmethod
    def validate_required_text_fields(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    @field_validator('short_description')
    @classmethod
    def validate_optional_text_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip()

    @field_validator('languages', mode='before')
    @classmethod
    def validate_languages_base(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('At least one language must be specified')
        return [lang.strip() for lang in v]

    @field_validator('platform_reviews_rating')
    @classmethod
    def validate_rating(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

    @field_validator('dollar_price', 'duration_h')
    @classmethod
    def validate_positive_decimal(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError('Value cannot be negative')
        return v

    @field_validator('platform_reviews_count', 'enrollment_count')
    @classmethod
    def validate_positive_integer(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Count cannot be negative')
        return v

class CreatorInput(CreatorBase):
    """Validation model for incoming creator data"""
    pass

class CreatorOutput(CreatorBase):
    """Validation model for creator data before saving to database"""
    id: UUID4

class LearningResourceInput(LearningResourceBase):
    """Validation model for incoming learning resource data"""
    
    @field_validator('languages')
    @classmethod
    def validate_languages_input(cls, v: List[str]) -> List[str]:
        """
        Accepts various language formats:
        - Full names ("English", "Spanish")
        - Native names ("Español")
        - ISO 639-1 codes ("en", "es")
        - ISO 639-2 codes ("eng", "spa")
        """
        if not v:
            raise ValueError('At least one language must be specified')
        
        clean_languages = []
        for lang in v:
            lang = lang.strip()
            # Try to find language by name or code
            try:
                # Try as 2-letter code
                language = pycountry.languages.get(alpha_2=lang.lower())
                if language:
                    clean_languages.append(language.alpha_2)
                    continue

                # Try as 3-letter code
                language = pycountry.languages.get(alpha_3=lang.lower())
                if language:
                    clean_languages.append(language.alpha_2)
                    continue

                # Try as name
                language = pycountry.languages.get(name=lang.title())
                if language and hasattr(language, 'alpha_2'):
                    clean_languages.append(language.alpha_2)
                    continue

                # If not found, keep original for manual review
                clean_languages.append(lang.lower())

            except (AttributeError, KeyError):
                clean_languages.append(lang.lower())

        return clean_languages

class LearningResourceOutput(LearningResourceBase):
    """Validation model for learning resource data before saving to database"""
    id: UUID4
    scraped_timestamp: datetime

    @field_validator('languages')
    @classmethod
    def validate_languages_output(cls, v: List[str]) -> List[str]:
        """Strictly validates that all languages are ISO 639-1 (2-letter) codes"""
        if not v:
            raise ValueError('At least one language must be specified')
        
        clean_languages = []
        for lang in v:
            lang = lang.strip().lower()
            # Verify it's a valid ISO 639-1 code
            language = pycountry.languages.get(alpha_2=lang)
            if not language:
                raise ValueError(f'Invalid ISO 639-1 language code: {lang}')
            clean_languages.append(lang)

        return clean_languages