import assemblyai as aai
import requests
import time
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AssemblyAIService:
    def __init__(self):
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        self.transcriber = aai.Transcriber()
    
    def transcribe_audio(
        self,
        audio_url: str,
        enable_speaker_diarization: bool = True,
        enable_sentiment_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio with speaker diarization and sentiment analysis
        """
        try:
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                speaker_labels=enable_speaker_diarization,
                sentiment_analysis=enable_sentiment_analysis,
                auto_chapters=True,
                punctuate=True,
                format_text=True
            )
            
            logger.info(f"Starting transcription for audio: {audio_url}")
            
            # Start transcription
            transcript = self.transcriber.transcribe(audio_url, config=config)
            
            # Wait for completion
            while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                time.sleep(5)
                transcript = self.transcriber.get_by_id(transcript.id)
                logger.info(f"Transcription status: {transcript.status}")
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
            
            # Process results
            result = {
                "transcript_text": transcript.text,
                "confidence": transcript.confidence,
                "audio_duration": transcript.audio_duration,
                "processing_time": None,  # Will be calculated by worker
                "speaker_diarization_results": None,
                "sentiment_analysis_results": None,
                "chapters": None
            }
            
            # Add speaker diarization results
            if enable_speaker_diarization and hasattr(transcript, 'utterances'):
                speaker_results = []
                for utterance in transcript.utterances:
                    speaker_results.append({
                        "speaker": utterance.speaker,
                        "text": utterance.text,
                        "start": utterance.start,
                        "end": utterance.end,
                        "confidence": utterance.confidence
                    })
                result["speaker_diarization_results"] = speaker_results
            
            # Add sentiment analysis results
            if enable_sentiment_analysis and hasattr(transcript, 'sentiment_analysis_results'):
                sentiment_results = []
                for sentiment in transcript.sentiment_analysis_results:
                    sentiment_results.append({
                        "text": sentiment.text,
                        "sentiment": sentiment.sentiment.value,
                        "confidence": sentiment.confidence,
                        "start": sentiment.start,
                        "end": sentiment.end
                    })
                result["sentiment_analysis_results"] = sentiment_results
            
            # Add chapters for summarization
            if hasattr(transcript, 'chapters') and transcript.chapters:
                chapters = []
                for chapter in transcript.chapters:
                    chapters.append({
                        "summary": chapter.summary,
                        "headline": chapter.headline,
                        "gist": chapter.gist,
                        "start": chapter.start,
                        "end": chapter.end
                    })
                result["chapters"] = chapters
            
            logger.info("Transcription completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {str(e)}")
            raise Exception(f"AssemblyAI transcription failed: {str(e)}")

assemblyai_service = AssemblyAIService()
