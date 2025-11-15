'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { conversationsAPI } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { ArrowLeft, AlertCircle } from 'lucide-react';

export default function HistoryPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await conversationsAPI.getHistory();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center">
          <Button variant="ghost" size="icon" onClick={() => router.push('/')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold text-green-700 ml-4">Conversation History</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading history...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <p className="text-gray-600">No conversations yet. Start a conversation on the home page!</p>
              <Button onClick={() => router.push('/')} className="mt-4">
                Start Conversation
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`bg-white rounded-lg shadow-md p-6 ${
                    conversation.is_emergency ? 'border-2 border-red-500' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        {conversation.is_emergency && (
                          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                        )}
                        <p className="text-sm text-gray-500">
                          {formatDate(conversation.created_at)}
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded p-3 mb-3">
                        <p className="text-sm font-semibold text-gray-700 mb-1">You asked:</p>
                        <p className="text-gray-800">{conversation.user_message}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 rounded p-4 mb-3">
                    <p className="text-sm font-semibold text-green-800 mb-2">
                      MediVoice Response:
                    </p>
                    <p className="text-gray-800 whitespace-pre-wrap">{conversation.ai_response}</p>
                  </div>

                  {conversation.symptoms_extracted && conversation.symptoms_extracted.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Symptoms detected:</p>
                      <div className="flex flex-wrap gap-2">
                        {conversation.symptoms_extracted.map((symptom: string, index: number) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs"
                          >
                            {symptom}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Provider: {conversation.llm_provider || 'N/A'}</span>
                    {conversation.response_time_ms && (
                      <span>Response time: {conversation.response_time_ms}ms</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
