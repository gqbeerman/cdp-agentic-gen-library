import { useState, useCallback, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import ThreadSidebar, { type Thread } from '@/components/ThreadSidebar'
import MessageList, { type Message } from '@/components/MessageList'
import ChatInput from '@/components/ChatInput'
import { Button } from '@/components/ui/button'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ChatPage() {
    const { user, session, signOut } = useAuth()
    const [threads, setThreads] = useState<Thread[]>([])
    const [activeThreadId, setActiveThreadId] = useState<string | null>(null)
    const [messages, setMessages] = useState<Message[]>([])
    const [streamingContent, setStreamingContent] = useState('')
    const [isStreaming, setIsStreaming] = useState(false)

    const getAuthHeaders = useCallback(() => {
        return {
            Authorization: `Bearer ${session?.access_token}`,
            'Content-Type': 'application/json',
        }
    }, [session])

    // Fetch threads on mount
    useEffect(() => {
        const fetchThreads = async () => {
            try {
                const res = await fetch(`${API_URL}/api/threads`, {
                    headers: getAuthHeaders(),
                })
                if (res.ok) {
                    const data = await res.json()
                    setThreads(data)
                }
            } catch (err) {
                console.error('Failed to fetch threads:', err)
            }
        }
        if (session) fetchThreads()
    }, [session, getAuthHeaders])

    // Fetch messages when active thread changes
    useEffect(() => {
        const fetchMessages = async () => {
            if (!activeThreadId) {
                setMessages([])
                return
            }
            try {
                const res = await fetch(
                    `${API_URL}/api/threads/${activeThreadId}/messages`,
                    { headers: getAuthHeaders() }
                )
                if (res.ok) {
                    const data = await res.json()
                    setMessages(data)
                }
            } catch (err) {
                console.error('Failed to fetch messages:', err)
            }
        }
        if (session) fetchMessages()
    }, [activeThreadId, session, getAuthHeaders])

    const handleNewThread = async () => {
        try {
            const res = await fetch(`${API_URL}/api/threads`, {
                method: 'POST',
                headers: getAuthHeaders(),
            })
            if (res.ok) {
                const thread = await res.json()
                setThreads((prev) => [thread, ...prev])
                setActiveThreadId(thread.id)
                setMessages([])
            }
        } catch (err) {
            console.error('Failed to create thread:', err)
        }
    }

    const handleDeleteThread = async (threadId: string) => {
        try {
            const res = await fetch(`${API_URL}/api/threads/${threadId}`, {
                method: 'DELETE',
                headers: getAuthHeaders(),
            })
            if (res.ok) {
                setThreads((prev) => prev.filter((t) => t.id !== threadId))
                if (activeThreadId === threadId) {
                    setActiveThreadId(null)
                    setMessages([])
                }
            }
        } catch (err) {
            console.error('Failed to delete thread:', err)
        }
    }

    const handleSendMessage = async (content: string) => {
        if (!activeThreadId || isStreaming) return

        // Add user message optimistically
        const userMessage: Message = {
            id: `temp-${Date.now()}`,
            role: 'user',
            content,
        }
        setMessages((prev) => [...prev, userMessage])
        setIsStreaming(true)
        setStreamingContent('')

        try {
            const res = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    thread_id: activeThreadId,
                    message: content,
                }),
            })

            if (!res.ok) throw new Error('Chat request failed')

            // Read SSE stream
            const reader = res.body?.getReader()
            const decoder = new TextDecoder()
            let fullContent = ''

            if (reader) {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    const lines = chunk.split('\n')

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6)
                            if (data === '[DONE]') continue

                            try {
                                const parsed = JSON.parse(data)
                                if (parsed.content) {
                                    fullContent += parsed.content
                                    setStreamingContent(fullContent)
                                }
                                if (parsed.citations_resolved) {
                                    fullContent = parsed.citations_resolved
                                    setStreamingContent(fullContent)
                                }
                                if (parsed.title_update) {
                                    setThreads((prev) =>
                                        prev.map((t) =>
                                            t.id === parsed.title_update.thread_id
                                                ? { ...t, title: parsed.title_update.title }
                                                : t
                                        )
                                    )
                                }
                            } catch {
                                // Skip non-JSON data lines
                            }
                        }
                    }
                }
            }

            // Finalize the assistant message
            if (fullContent) {
                const assistantMessage: Message = {
                    id: `msg-${Date.now()}`,
                    role: 'assistant',
                    content: fullContent,
                }
                setMessages((prev) => [...prev, assistantMessage])
            }
        } catch (err) {
            console.error('Failed to send message:', err)
        } finally {
            setStreamingContent('')
            setIsStreaming(false)
        }
    }

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <ThreadSidebar
                threads={threads}
                activeThreadId={activeThreadId}
                onSelectThread={setActiveThreadId}
                onNewThread={handleNewThread}
                onDeleteThread={handleDeleteThread}
            />

            {/* Main chat area */}
            <div className="flex flex-1 flex-col">
                {/* Header */}
                <header className="flex items-center justify-between border-b px-6 py-3">
                    <h1 className="text-lg font-semibold">📚 Agentic RAG Library</h1>
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-muted-foreground">
                            {user?.email}
                        </span>
                        <Button variant="ghost" size="sm" onClick={signOut}>
                            Sign Out
                        </Button>
                    </div>
                </header>

                {/* Messages */}
                {activeThreadId ? (
                    <>
                        <MessageList
                            messages={messages}
                            streamingContent={streamingContent || undefined}
                            isThinking={isStreaming}
                        />
                        <ChatInput
                            onSend={handleSendMessage}
                            disabled={isStreaming}
                        />
                    </>
                ) : (
                    <div className="flex flex-1 items-center justify-center text-muted-foreground">
                        <div className="text-center space-y-4">
                            <p className="text-xl font-medium">Welcome to Agentic RAG Library</p>
                            <p className="text-sm">
                                Select a conversation from the sidebar or start a new one.
                            </p>
                            <Button onClick={handleNewThread}>Start a New Chat</Button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
