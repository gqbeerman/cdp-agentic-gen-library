import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'
import { useAuth } from './AuthContext'

export interface Document {
    id: string
    filename: string
    file_type: string
    file_size: number
    status: 'uploaded' | 'processing' | 'ready' | 'error'
    error_message?: string
    chunk_count: number
    created_at: string
}

interface DocumentStatusContextType {
    documents: Document[]
    isLoading: boolean
    isProcessing: boolean
    error: string | null
    refreshDocuments: (background?: boolean) => Promise<void>
}

const DocumentStatusContext = createContext<DocumentStatusContextType | undefined>(undefined)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function DocumentStatusProvider({ children }: { children: React.ReactNode }) {
    const { session } = useAuth()
    const [documents, setDocuments] = useState<Document[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const isProcessing = documents.some((doc) => doc.status === 'processing' || doc.status === 'uploaded')

    const fetchDocuments = async (background: boolean = false) => {
        if (!session) return
        try {
            if (!background) setIsLoading(true)
            const response = await fetch(`${API_URL}/api/documents`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`,
                }
            })
            if (!response.ok) throw new Error('Failed to fetch documents')
            const data = await response.json()
            setDocuments(data)
            setError(null)
        } catch (err: any) {
            setError(err.message)
        } finally {
            if (!background) setIsLoading(false)
        }
    }

    useEffect(() => {
        if (session) {
            fetchDocuments()
        } else {
            setDocuments([])
            setIsLoading(false)
        }
    }, [session])

    useEffect(() => {
        if (!session) return

        const channel = supabase
            .channel('global-schema-db-changes')
            .on(
                'postgres_changes',
                { event: '*', schema: 'public', table: 'documents' },
                (payload) => {
                    console.log('Global realtime update:', payload)

                    if (payload.eventType === 'INSERT') {
                        const newDoc = payload.new as Document
                        setDocuments((prev) => [newDoc, ...prev])
                        if (newDoc.status === 'uploaded' || newDoc.status === 'processing') {
                            toast.info(`Processing started for ${newDoc.filename}`, { id: `processing-${newDoc.id}` })
                        }
                    } else if (payload.eventType === 'UPDATE') {
                        const updatedDoc = payload.new as Document

                        setDocuments((prev) => {
                            const oldDoc = prev.find(d => d.id === updatedDoc.id)

                            // Check if status changed to ready
                            if (oldDoc && oldDoc.status !== 'ready' && updatedDoc.status === 'ready') {
                                toast.success(`${updatedDoc.filename} is ready for querying!`, { id: `ready-${updatedDoc.id}` })
                            } else if (oldDoc && oldDoc.status !== 'error' && updatedDoc.status === 'error') {
                                toast.error(`Failed to process ${updatedDoc.filename}`, { id: `error-${updatedDoc.id}` })
                            }

                            return prev.map((doc) => (doc.id === updatedDoc.id ? updatedDoc : doc))
                        })
                    } else if (payload.eventType === 'DELETE') {
                        setDocuments((prev) => prev.filter((doc) => doc.id !== payload.old.id))
                    }
                }
            )
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [session])

    return (
        <DocumentStatusContext.Provider value={{ documents, isLoading, isProcessing, error, refreshDocuments: fetchDocuments }}>
            {children}
        </DocumentStatusContext.Provider>
    )
}

export function useDocumentStatus() {
    const context = useContext(DocumentStatusContext)
    if (context === undefined) {
        throw new Error('useDocumentStatus must be used within a DocumentStatusProvider')
    }
    return context
}
