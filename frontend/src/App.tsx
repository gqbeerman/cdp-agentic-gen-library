import { useState } from 'react'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import AuthPage from '@/pages/AuthPage'
import ChatPage from '@/pages/ChatPage'
import IngestionPage from '@/pages/IngestionPage'
import { Database, MessageSquare } from 'lucide-react'
import './App.css'

function AppContent() {
  const { user, loading } = useAuth()
  const [currentView, setCurrentView] = useState<'chat' | 'documents'>('chat')

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex h-14 shrink-0 items-center justify-between border-b bg-card px-6">
        <div className="flex items-center gap-2 font-semibold">
          <div className="rounded-full bg-primary/10 p-1">
            <MessageSquare className="h-4 w-4 text-primary" />
          </div>
          <span>CDP Agentic RAG</span>
        </div>

        <nav className="flex gap-1 bg-muted/50 p-1 rounded-lg">
          <button
            onClick={() => setCurrentView('chat')}
            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${currentView === 'chat'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
          >
            <MessageSquare className="h-4 w-4" />
            Chat
          </button>
          <button
            onClick={() => setCurrentView('documents')}
            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${currentView === 'documents'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
          >
            <Database className="h-4 w-4" />
            Knowledge Base
          </button>
        </nav>

        <div className="w-[140px]" /> {/* Spacer to balance the header flex-between */}
      </header>

      <main className="flex-1 overflow-hidden">
        {currentView === 'chat' ? <ChatPage /> : <IngestionPage />}
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
