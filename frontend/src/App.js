import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  BookOpen, Play, Pause, Download, Loader2, 
  RefreshCw, ChevronRight, Volume2, GraduationCap,
  AlertCircle, CheckCircle, LogOut, Smartphone, Eye, EyeOff,
  Clock, TrendingUp, Award
} from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || '';

const LANGUAGES = [
  { code: 'mr', name: 'मराठी', label: 'Marathi' },
  { code: 'hi', name: 'हिंदी', label: 'Hindi' },
  { code: 'en', name: 'English', label: 'English' }
];

// Session Management Helper
const SESSION_CHECK_INTERVAL = 60000; // Check every 60 seconds
const SESSION_TIMEOUT_WARNING = 10000; // Warn 10 seconds before timeout
const MAX_RECONNECT_ATTEMPTS = 5;

function App() {
  const [curriculum, setCurriculum] = useState({});
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [language, setLanguage] = useState('mr');
  const [loading, setLoading] = useState(false);
  const [teaching, setTeaching] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [studentId, setStudentId] = useState(null);
  const [studentName, setStudentName] = useState('');
  const [showLoginForm, setShowLoginForm] = useState(true);
  const [sessionValid, setSessionValid] = useState(false);
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(0);
  const [progress, setProgress] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [apiStatus, setApiStatus] = useState('healthy');
  const audioRef = useRef(null);
  const sessionCheckRef = useRef(null);
  const sessionWarningRef = useRef(null);

  // Health check and reconnect logic
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get(apiUrl('/health'), { timeout: 5000 });
        if (response.data.status === 'healthy') {
          setApiStatus('healthy');
          setReconnectAttempts(0);
        } else {
          setApiStatus('degraded');
        }
      } catch (err) {
        setApiStatus('offline');
        // Try to reconnect
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          setTimeout(() => setReconnectAttempts(reconnectAttempts + 1), 5000);
        }
      }
    };

    checkHealth();
    const healthInterval = setInterval(checkHealth, 30000);
    return () => clearInterval(healthInterval);
  }, [reconnectAttempts]);

  // Session validation and timeout handling
  useEffect(() => {
    if (!studentId) return;

    const validateSession = async () => {
      try {
        const res = await axios.get(apiUrl(`/api/session/validate/${studentId}`), { timeout: 5000 });
        if (res.data.valid) {
          setSessionValid(true);
          setSessionTimeRemaining(res.data.remaining_minutes * 60);
        } else {
          handleSessionExpired();
        }
      } catch (err) {
        console.log('Session validation failed:', err.message);
      }
    };

    validateSession();
    sessionCheckRef.current = setInterval(validateSession, SESSION_CHECK_INTERVAL);
    
    return () => {
      if (sessionCheckRef.current) clearInterval(sessionCheckRef.current);
    };
  }, [studentId]);

  // Session timeout warning
  useEffect(() => {
    if (sessionTimeRemaining <= 0 || sessionTimeRemaining > SESSION_TIMEOUT_WARNING) return;

    if (!sessionWarningRef.current) {
      sessionWarningRef.current = true;
      setError('⚠️ Your session will expire soon. Please save your work or click to extend session.');
    }
  }, [sessionTimeRemaining]);

  const apiUrl = (path) => `${API_URL || ''}${path}`;

  const fetchCurriculum = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get(apiUrl('/api/curriculum'), { timeout: 10000 });
      setCurriculum(res.data);
      setSubjects(Object.keys(res.data));
    } catch (err) {
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        setError(`Connection failed. Retrying... (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        setTimeout(() => {
          setReconnectAttempts(reconnectAttempts + 1);
          fetchCurriculum();
        }, 3000);
      } else {
        setError('Cannot connect to server. Please check your internet connection and refresh the page.');
      }
    } finally {
      setLoading(false);
    }
  };

  const registerStudent = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData(e.target);
      const newStudentId = formData.get('studentId');
      const newStudentName = formData.get('studentName');
      const email = formData.get('email');

      const res = await axios.post(apiUrl('/api/session/create'), {
        student_id: newStudentId,
        name: newStudentName,
        email: email
      }, { timeout: 10000 });

      setStudentId(newStudentId);
      setStudentName(newStudentName);
      setShowLoginForm(false);
      setSessionValid(true);
      await fetchCurriculum();
    } catch (err) {
      console.error('Registration error', err);
      setError(err.response?.data?.message || err.message || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSessionExpired = () => {
    setSessionValid(false);
    setStudentId(null);
    setShowLoginForm(true);
    setError('Your session has expired. Please login again.');
  };

  const handleLogout = async () => {
    try {
      if (studentId) {
        await axios.post(apiUrl(`/api/session/close/${studentId}`), {}, { timeout: 5000 });
      }
    } catch (err) {
      console.log('Error closing session:', err);
    }
    
    setStudentId(null);
    setShowLoginForm(true);
    setSessionValid(false);
    setProgress(null);
    setReconnectAttempts(0);
  };

  const startLearning = async (chapter) => {
    if (!selectedSubject || !studentId) return;
    
    setSelectedChapter(chapter);
    setTeaching(true);
    setResponse(null);
    setError(null);
    
    try {
      const res = await axios.post(apiUrl('/api/learn'), {
        subject: selectedSubject,
        chapter: chapter.title,
        language: language
      }, { timeout: 30000 });
      
      setResponse(res.data);
      sessionWarningRef.current = false;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get explanation. Please try again.');
    } finally {
      setTeaching(false);
    }
  };

  const markChapterComplete = async () => {
    if (!studentId || !selectedChapter) return;
    
    try {
      await axios.post(apiUrl('/api/mark-complete'), {
        student_id: studentId,
        subject: selectedSubject,
        chapter: selectedChapter.title
      }, { timeout: 10000 });
      
      setError(null);
      await loadStudentProgress();
    } catch (err) {
      console.log('Could not save progress:', err.message);
    }
  };

  const loadStudentProgress = async () => {
    if (!studentId) return;
    
    try {
      const res = await axios.get(apiUrl(`/api/student-progress/${studentId}`), { timeout: 10000 });
      setProgress(res.data.progress);
    } catch (err) {
      console.log('Could not load progress:', err.message);
    }
  };

  const toggleAudio = () => {
    if (response?.audio_url && audioRef.current) {
      if (playing) {
        audioRef.current.pause();
        setPlaying(false);
      } else {
        audioRef.current.src = apiUrl(response.audio_url);
        audioRef.current.play().catch(err => {
          console.log('Play failed:', err);
        });
        setPlaying(true);
      }
    }
  };

  const handleAudioEnded = () => {
    setPlaying(false);
  };

  // Load progress when student logs in
  useEffect(() => {
    if (studentId && sessionValid) {
      loadStudentProgress();
    }
  }, [studentId, sessionValid]);

  // Auto-play audio when response is received
  useEffect(() => {
    if (response?.audio_url && audioRef.current) {
      audioRef.current.src = apiUrl(response.audio_url);
      audioRef.current.play().catch(err => {
        console.log('Auto-play failed:', err);
      });
      setPlaying(true);
    }
  }, [response]);

  // Login Form
  if (showLoginForm) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <GraduationCap className="w-16 h-16 text-blue-600 mx-auto mb-3" />
              <h1 className="text-3xl font-bold text-gray-800">महाराष्ट्र बोर्ड</h1>
              <p className="text-gray-600 mt-2">SSC AI Tutor</p>
              <p className="text-sm text-gray-500 mt-4">Welcome to your personal learning platform</p>
            </div>

            {apiStatus === 'offline' && (
              <div className="bg-red-50 border border-red-300 text-red-700 p-3 rounded-xl mb-6 text-sm flex items-center gap-2">
                <AlertCircle size={18} />
                Server is unavailable. Retrying...
              </div>
            )}

            <form onSubmit={registerStudent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Roll Number / Student ID</label>
                <input
                  type="text"
                  name="studentId"
                  placeholder="e.g., SSC001"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  name="studentName"
                  placeholder="Your name"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  placeholder="your@email.com"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  disabled={loading}
                />
              </div>

              {error && (
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-3 rounded-lg text-sm flex items-center gap-2">
                  <AlertCircle size={18} />
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="animate-spin" size={20} /> : <span>Start Learning</span>}
              </button>
            </form>

            <p className="text-center text-gray-500 text-xs mt-6">
              Your progress is automatically saved to your account
            </p>
          </div>
        </div>
      </div>
    );
  }

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
      <header className="bg-gradient-to-r from-blue-800 via-indigo-800 to-purple-800 text-white shadow-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3 flex-1">
              <GraduationCap size={40} className="text-yellow-400" />
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">महाराष्ट्र बोर्ड SSC AI Tutor</h1>
                <p className="text-blue-200 text-sm">
                  📚 {studentName ? `Hello, ${studentName}` : 'Maharashtra Board 10th Class'}
                </p>
              </div>
            </div>
            
            {/* API Status Badge */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${apiStatus === 'healthy' ? 'bg-green-400' : apiStatus === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'}`} />
              <span className="text-xs font-medium">{apiStatus === 'healthy' ? 'Connected' : apiStatus === 'degraded' ? 'Slow' : 'Offline'}</span>
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

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-white transition-all text-sm font-medium"
            >
              <LogOut size={18} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>

          {/* Session Status & Time Remaining */}
          {sessionTimeRemaining > 0 && sessionTimeRemaining < SESSION_TIMEOUT_WARNING && (
            <div className="mt-3 bg-yellow-400/20 border border-yellow-300 text-yellow-800 p-2 rounded-lg text-sm flex items-center gap-2">
              <Clock size={16} />
              Session ending soon. Save your work!
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 flex flex-col lg:flex-row gap-6">
        
        {/* Sidebar - Subjects, Chapters, Progress */}
        <aside className="lg:w-96 space-y-6">
          {/* Progress Card */}
          {progress && (
            <div className="bg-white rounded-2xl shadow-xl p-5">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-gray-800">
                <TrendingUp size={24} className="text-green-600" />
                Your Progress
              </h3>
              <div className="space-y-3">
                {progress.subjects_progress && Object.entries(progress.subjects_progress).map(([subject, count]) => (
                  <div key={subject}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700">{subject}</span>
                      <span className="text-blue-600 font-bold">{count} chapters</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min((count / 10) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              {progress.quiz_scores && Object.keys(progress.quiz_scores).length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center gap-2 mb-2">
                    <Award size={18} className="text-yellow-600" />
                    <span className="font-medium text-gray-700">Quiz Performance</span>
                  </div>
                  {Object.entries(progress.quiz_scores).map(([subject, score]) => (
                    <div key={subject} className="text-sm text-gray-600 flex justify-between">
                      <span>{subject}</span>
                      <span className="font-bold text-blue-600">{score.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Subjects & Chapters */}
          <div className="bg-white rounded-2xl shadow-xl p-5 max-h-[600px] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800 sticky top-0 bg-white pb-3">
              <BookOpen size={24} className="text-blue-600" />
              विषय निवडा (Select Subject)
            </h2>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 flex items-center gap-2 text-sm">
                <AlertCircle size={18} />
                <span>{error}</span>
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
          </div>
        </aside>

        {/* Main Content - AI Teacher */}
        <section className="flex-1">
          <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 min-h-[600px]">
            
            {!selectedSubject ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <BookOpen size={100} className="mb-6 opacity-20" />
                <h2 className="text-2xl font-medium">Welcome to AI Tutor!</h2>
                <p className="mt-2 text-center text-gray-600">Select a Subject from the left to start learning</p>
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
                            ? 'bg-green-600 animate-pulse' 
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
                        onClick={() => markChapterComplete()}
                        className="flex items-center gap-3 px-6 py-4 rounded-full bg-green-100 text-green-700 font-medium hover:bg-green-200 transition-all"
                      >
                        <CheckCircle size={20} />
                        Mark Complete
                      </button>
                      
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
                        💡 <strong>Tip:</strong> You can change the language above to hear explanations in Marathi, Hindi, or English. All your progress is automatically saved!
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
          <p className="text-gray-500 text-sm mt-2">✨ Always Available • Smart Explanations • Progress Tracked • Board Questions Included</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

