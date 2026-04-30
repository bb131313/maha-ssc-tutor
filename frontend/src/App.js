import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  BookOpen, Play, Pause, Download, Loader2, 
  RefreshCw, ChevronRight, Volume2, GraduationCap,
  AlertCircle, CheckCircle
} from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const LANGUAGES = [
  { code: 'mr', name: 'मराठी', label: 'Marathi' },
  { code: 'hi', name: 'हिंदी', label: 'Hindi' },
  { code: 'en', name: 'English', label: 'English' }
];

function App() {
  const [curriculum, setCurriculum] = useState({});
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [language, setLanguage] = useState('mr');
  const [loading, setLoading] = useState(true);
  const [teaching, setTeaching] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    fetchCurriculum();
  }, []);

  const fetchCurriculum = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/api/curriculum`);
      setCurriculum(res.data);
      setSubjects(Object.keys(res.data));
    } catch (err) {
      setError('Cannot connect to server. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const startLearning = async (chapter) => {
    if (!selectedSubject) return;
    
    setSelectedChapter(chapter);
    setTeaching(true);
    setResponse(null);
    setError(null);
    
    try {
      const res = await axios.post(`${API_URL}/api/learn`, {
        subject: selectedSubject,
        chapter: chapter.title,
        language: language
      });
      setResponse(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get explanation');
    } finally {
      setTeaching(false);
    }
  };

  const toggleAudio = () => {
    if (response?.audio_url && audioRef.current) {
      audioRef.current.src = `${API_URL}${response.audio_url}`;
      audioRef.current.play();
      setPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setPlaying(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <GraduationCap className="w-20 h-20 text-white mx-auto mb-4 animate-bounce" />
          <Loader2 className="animate-spin w-10 h-10 text-blue-300 mx-auto" />
          <p className="text-white text-xl mt-4">Loading Maharashtra Board...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <audio 
        ref={audioRef} 
        onEnded={handleAudioEnded}
        onError={() => setPlaying(false)}
      />
      
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-800 via-indigo-800 to-purple-800 text-white shadow-xl">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <GraduationCap size={40} className="text-yellow-400" />
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">महाराष्ट्र बोर्ड SSC AI Tutor</h1>
                <p className="text-blue-200 text-sm">Maharashtra Board 10th Class</p>
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="flex gap-2 bg-white/10 p-1 rounded-full">
              {LANGUAGES.map(lang => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    language === lang.code
                      ? 'bg-white text-blue-800 shadow-lg'
                      : 'text-white hover:bg-white/20'
                  }`}
                >
                  {lang.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 flex flex-col lg:flex-row gap-6">
        
        {/* Sidebar - Subjects and Chapters */}
        <aside className="lg:w-96 bg-white rounded-2xl shadow-xl p-5 h-fit sticky top-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
            <BookOpen size={24} className="text-blue-600" />
            विषय निवडा (Select Subject)
          </h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 flex items-center gap-2">
              <AlertCircle size={18} />
              <span className="text-sm">{error}</span>
            </div>
          )}
          
          <div className="space-y-2">
            {subjects.map(subject => (
              <div key={subject}>
                <button
                  onClick={() => {
                    setSelectedSubject(subject);
                    setSelectedChapter(null);
                    setResponse(null);
                  }}
                  className={`w-full text-left p-4 rounded-xl font-medium transition-all flex items-center justify-between ${
                    selectedSubject === subject
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <span>{subject}</span>
                  <ChevronRight 
                    size={20} 
                    className={`transition-transform ${selectedSubject === subject ? 'rotate-90' : ''}`}
                  />
                </button>
                
                {selectedSubject === subject && curriculum[subject]?.chapters && (
                  <div className="ml-2 mt-2 space-y-1 max-h-96 overflow-y-auto pr-2">
                    {curriculum[subject].chapters.map(chapter => (
                      <div 
                        key={chapter.id} 
                        onClick={() => startLearning(chapter)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          selectedChapter?.id === chapter.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <p className="font-medium text-sm text-gray-800">{chapter.title}</p>
                          {selectedChapter?.id === chapter.id && (
                            <CheckCircle size={16} className="text-blue-600 flex-shrink-0" />
                          )}
                        </div>
                        <a 
                          href={chapter.link} 
                          target="_blank" 
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="text-xs text-blue-600 flex items-center gap-1 mt-2 hover:underline"
                        >
                          <Download size={12} /> 
                          <span className="hidden sm:inline">Textbook</span>
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content - AI Teacher */}
        <section className="flex-1">
          <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 min-h-[600px]">
            
            {!selectedSubject ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <BookOpen size={100} className="mb-6 opacity-20" />
                <h2 className="text-2xl font-medium">Welcome to AI Tutor!</h2>
                <p className="mt-2 text-center">Select a Subject from the left to start learning</p>
                <div className="mt-6 bg-blue-50 p-4 rounded-xl max-w-md">
                  <p className="text-sm text-blue-800 text-center">
                    🎓 Click any subject to see chapters. Then click a chapter to get AI-powered explanation with voice!
                  </p>
                </div>
              </div>
            ) : !selectedChapter ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-500">
                <GraduationCap size={80} className="mb-4 opacity-50" />
                <h2 className="text-2xl font-medium">{selectedSubject}</h2>
                <p className="mt-2">Select a chapter from the list to begin your lesson</p>
              </div>
            ) : (
              <>
                {/* Chapter Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-4 border-b">
                  <div>
                    <span className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full font-medium">
                      {selectedSubject}
                    </span>
                    <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mt-2">
                      {selectedChapter.title}
                    </h2>
                  </div>
                  
                  {teaching && (
                    <div className="flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full">
                      <RefreshCw className="animate-spin" size={18} />
                      <span className="font-medium">AI Teacher is preparing...</span>
                    </div>
                  )}
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 flex items-center gap-3">
                    <AlertCircle size={24} />
                    <div>
                      <p className="font-medium">Error</p>
                      <p className="text-sm">{error}</p>
                    </div>
                  </div>
                )}

                {/* Explanation Content */}
                {response && (
                  <>
                    <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 md:p-8 rounded-2xl border border-blue-100 mb-6">
                      <div className="flex items-center gap-2 mb-4">
                        <Volume2 size={20} className="text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">AI Explanation</span>
                      </div>
                      <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed text-base md:text-lg">
                        {response.explanation}
                      </pre>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-4">
                      <button
                        onClick={toggleAudio}
                        disabled={!response.audio_url}
                        className={`flex items-center gap-3 px-6 py-4 rounded-full text-white font-medium text-lg shadow-lg transition-all ${
                          playing 
                            ? 'bg-green-600 animate-pulse-audio' 
                            : 'bg-green-600 hover:bg-green-700 hover:shadow-xl'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {playing ? (
                          <>
                            <Pause size={24} />
                            Playing...
                          </>
                        ) : (
                          <>
                            <Play size={24} />
                            Listen to Explanation
                          </>
                        )}
                      </button>
                      
                      <a 
                        href={response.textbook_link} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center gap-3 px-6 py-4 rounded-full bg-blue-600 text-white font-medium text-lg hover:bg-blue-700 shadow-lg transition-all"
                      >
                        <BookOpen size={24} />
                        Open Ebalbharati Textbook
                      </a>
                      
                      <button
                        onClick={() => startLearning(selectedChapter)}
                        className="flex items-center gap-3 px-6 py-4 rounded-full bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-all"
                      >
                        <RefreshCw size={20} />
                        Explain Again
                      </button>
                    </div>
                    
                    {/* Info Box */}
                    <div className="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-xl">
                      <p className="text-sm text-yellow-800">
                        💡 <strong>Tip:</strong> You can change the language above to hear explanations in Marathi, Hindi, or English.
                      </p>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">Maharashtra Board SSC AI Tutor - Built for Students</p>
          <p className="text-gray-500 text-sm mt-2">Powered by AI • Ebalbharati Textbooks</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
