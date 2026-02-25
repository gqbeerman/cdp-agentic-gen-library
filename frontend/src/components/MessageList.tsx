import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import ThinkingIndicator from './ThinkingIndicator'

export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
}

interface MessageListProps {
    messages: Message[]
    streamingContent?: string
    isThinking?: boolean
}

export default function MessageList({
    messages,
    streamingContent,
    isThinking,
}: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, streamingContent, isThinking])

    if (messages.length === 0 && !streamingContent) {
        return (
            <div className="flex flex-1 items-center justify-center text-muted-foreground">
                <div className="text-center space-y-2">
                    <p className="text-lg font-medium">Start a conversation</p>
                    <p className="text-sm">Send a message to begin chatting.</p>
                </div>
            </div>
        )
    }

    return (
        <ScrollArea className="flex-1">
            <div className="mx-auto max-w-3xl space-y-6 p-4">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted text-foreground'
                                }`}
                        >
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                        </div>
                    </div>
                ))}

                {isThinking && !streamingContent && (
                    <ThinkingIndicator />
                )}

                {streamingContent && (
                    <div className="flex justify-start">
                        <div className="max-w-[80%] rounded-2xl bg-muted px-4 py-3 text-sm leading-relaxed text-foreground">
                            <div className="whitespace-pre-wrap">
                                {streamingContent}
                                <span className="inline-block h-4 w-1 animate-pulse bg-foreground ml-0.5" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>
        </ScrollArea>
    )
}
