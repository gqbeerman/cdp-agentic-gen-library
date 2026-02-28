import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Settings } from 'lucide-react'
import { useState } from 'react'
import { SettingsModal } from './SettingsModal'

export interface Thread {
    id: string
    thread_id: string
    title: string
    created_at: string
}

interface ThreadSidebarProps {
    threads: Thread[]
    activeThreadId: string | null
    onSelectThread: (threadId: string) => void
    onNewThread: () => void
    onDeleteThread: (threadId: string) => void
}

export default function ThreadSidebar({
    threads,
    activeThreadId,
    onSelectThread,
    onNewThread,
    onDeleteThread,
}: ThreadSidebarProps) {
    const [isSettingsOpen, setIsSettingsOpen] = useState(false)

    return (
        <div className="flex h-full w-64 flex-col border-r bg-muted/30">
            <div className="p-4">
                <Button onClick={onNewThread} className="w-full" variant="outline">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="mr-2 h-4 w-4"
                    >
                        <path d="M12 5v14" />
                        <path d="M5 12h14" />
                    </svg>
                    New Chat
                </Button>
            </div>
            <Separator />
            <ScrollArea className="flex-1">
                <div className="p-2 space-y-1">
                    {threads.map((thread) => (
                        <div
                            key={thread.id}
                            className={`group grid grid-cols-[1fr_auto] items-center gap-2 rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors ${activeThreadId === thread.id
                                ? 'bg-accent text-accent-foreground'
                                : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                                }`}
                            onClick={() => onSelectThread(thread.id)}
                        >
                            <span className="truncate">{thread.title}</span>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    onDeleteThread(thread.id)
                                }}
                                className="text-muted-foreground hover:text-destructive flex items-center justify-center rounded p-1 hover:bg-destructive/10"
                                title="Delete thread"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth={2}
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="h-4 w-4"
                                >
                                    <path d="M3 6h18" />
                                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                                </svg>
                            </button>
                        </div>
                    ))}
                    {threads.length === 0 && (
                        <p className="px-3 py-4 text-center text-xs text-muted-foreground">
                            No conversations yet
                        </p>
                    )}
                </div>
            </ScrollArea>

            <Separator />
            <div className="p-4">
                <Button
                    variant="ghost"
                    className="w-full justify-start text-muted-foreground"
                    onClick={() => setIsSettingsOpen(true)}
                >
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                </Button>
            </div>

            <SettingsModal
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
            />
        </div>
    )
}
