'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { VoiceRecorder } from '@/components/voice-recorder';
import { Button } from '@/components/ui/button';
import { voiceAPI, authAPI } from '@/lib/api';
import { MessageSquare, Calendar, History, LogOut } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/login');
      return;
    }

    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await authAPI.getProfile();
      setUser(userData);
    } catch (error) {
      console.error('Failed to load user:', error);
      router.push('/auth/login');
    }
  };

  const handleVoiceSubmit = async (audioData: string) => {
    setIsLoading(true);
    setResponse(null);

    try {
      const result = await voiceAPI.interact({ audio_data: audioData });
      setResponse(result);
    } catch (error: any) {
      console.error('Voice interaction error:', error);
      alert(error.response?.data?.detail || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim()) return;

    setIsLoading(true);
    setResponse(null);

    try {
      const result = await voiceAPI.interact({ text_message: textInput });
      setResponse(result);
      setTextInput('');
    } catch (error: any) {
      console.error('Text interaction error:', error);
      alert(error.response?.data?.detail || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    router.push('/auth/login');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-green-700">MediVoice GH</h1>
            <p className="text-sm text-gray-600">AI Health Advisor for Ghana</p>
          </div>
          <div className="flex items-center space-x-4">
            <p className="text-sm text-gray-600">Welcome, {user.full_name || user.email}</p>
            <Button variant="ghost" size="icon" onClick={() => router.push('/history')}>
              <History className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => router.push('/appointments')}>
              <Calendar className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          {/* Instructions */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-3 text-green-700">
              How can I help you today?
            </h2>
            <p className="text-gray-600 mb-4">
              Describe your symptoms using voice or text. I'll provide health information and advice.
            </p>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm">
              <p className="font-semibold text-yellow-800">Important:</p>
              <p className="text-yellow-700">
                This is for information only. Always consult a qualified healthcare professional for medical advice.
                In emergencies, call 112 immediately.
              </p>
            </div>
          </div>

          {/* Voice Input */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <MessageSquare className="w-5 h-5 mr-2 text-green-600" />
              Voice Message
            </h3>
            <VoiceRecorder onSend={handleVoiceSubmit} isLoading={isLoading} />
          </div>

          {/* Text Input */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Or Type Your Message</h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
                placeholder="Describe your symptoms..."
                className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                disabled={isLoading}
              />
              <Button onClick={handleTextSubmit} disabled={isLoading || !textInput.trim()}>
                Send
              </Button>
            </div>
          </div>

          {/* Response */}
          {isLoading && (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Analyzing your symptoms...</p>
            </div>
          )}

          {response && !isLoading && (
            <div className={`rounded-lg shadow-md p-6 ${response.is_emergency ? 'bg-red-50 border-2 border-red-500' : 'bg-white'}`}>
              {response.is_emergency && (
                <div className="mb-4 text-center">
                  <p className="text-3xl mb-2">🚨</p>
                  <p className="text-xl font-bold text-red-600">EMERGENCY DETECTED</p>
                </div>
              )}

              <div className="prose max-w-none mb-4">
                <p className="whitespace-pre-wrap">{response.text_response}</p>
              </div>

              {response.symptoms_detected && response.symptoms_detected.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Symptoms detected:</p>
                  <div className="flex flex-wrap gap-2">
                    {response.symptoms_detected.map((symptom: string, index: number) => (
                      <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        {symptom}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {!response.is_emergency && (
                <div className="mt-4 pt-4 border-t">
                  <Button onClick={() => router.push('/appointments')} variant="outline" className="w-full">
                    <Calendar className="w-4 h-4 mr-2" />
                    Book an Appointment
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>MediVoice GH - AI Voice Health Advisor for Ghana</p>
          <p className="mt-1">Created by John Evans Okyere</p>
        </div>
      </footer>
    </div>
  );
}
