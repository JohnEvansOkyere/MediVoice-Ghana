'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Mic, Square, Send } from 'lucide-react';

interface VoiceRecorderProps {
  onSend: (audioData: string) => void;
  isLoading: boolean;
}

export function VoiceRecorder({ onSend, isLoading }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSend = async () => {
    if (!audioBlob) return;

    // Convert blob to base64
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      const base64Data = base64String.split(',')[1]; // Remove data:audio/webm;base64, prefix
      onSend(base64Data);
      setAudioBlob(null);
    };
    reader.readAsDataURL(audioBlob);
  };

  const handleReset = () => {
    setAudioBlob(null);
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="flex items-center space-x-4">
        {!audioBlob && !isRecording && (
          <Button
            onClick={startRecording}
            disabled={isLoading}
            size="lg"
            className="rounded-full w-20 h-20"
          >
            <Mic className="w-8 h-8" />
          </Button>
        )}

        {isRecording && (
          <Button
            onClick={stopRecording}
            variant="destructive"
            size="lg"
            className="rounded-full w-20 h-20 animate-pulse"
          >
            <Square className="w-8 h-8" />
          </Button>
        )}

        {audioBlob && !isRecording && (
          <div className="flex space-x-2">
            <Button onClick={handleReset} variant="outline">
              Re-record
            </Button>
            <Button onClick={handleSend} disabled={isLoading}>
              <Send className="w-4 h-4 mr-2" />
              Send
            </Button>
          </div>
        )}
      </div>

      {isRecording && (
        <p className="text-sm text-muted-foreground animate-pulse">
          Recording... Click stop when done
        </p>
      )}

      {audioBlob && !isRecording && (
        <div className="flex flex-col items-center space-y-2">
          <audio controls src={URL.createObjectURL(audioBlob)} className="w-full max-w-md" />
          <p className="text-sm text-muted-foreground">
            Review your message and click Send
          </p>
        </div>
      )}
    </div>
  );
}
