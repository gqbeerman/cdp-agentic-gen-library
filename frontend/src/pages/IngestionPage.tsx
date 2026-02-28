import { useState } from 'react'
import { FileText, Loader2, Trash2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

import { supabase } from '@/lib/supabase'
import FileUploadZone from '@/components/FileUploadZone'
import { useDocumentStatus } from '@/contexts/DocumentStatusProvider'

export default function IngestionPage() {
    const { documents, isLoading, error: statusError } = useDocumentStatus()
    const [localError, setLocalError] = useState<string | null>(null)

    const error = statusError || localError

    const handleDelete = async (id: string) => {
        try {
            const { data: { session } } = await supabase.auth.getSession()
            if (!session) throw new Error('Not authenticated')

            const response = await fetch(`http://localhost:8000/api/documents/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`,
                }
            })
            if (!response.ok) throw new Error('Failed to delete document')
            // Note: Realtime subscription will handle removing it from the list
        } catch (err: any) {
            alert(err.message)
        }
    }

    const formatBytes = (bytes: number, decimals = 2) => {
        if (!+bytes) return '0 Bytes'
        const k = 1024
        const dm = decimals < 0 ? 0 : decimals
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'uploaded': return 'bg-blue-100 text-blue-800 border-blue-200'
            case 'processing': return 'bg-amber-100 text-amber-800 border-amber-200'
            case 'ready': return 'bg-green-100 text-green-800 border-green-200'
            case 'error': return 'bg-red-100 text-red-800 border-red-200'
            default: return 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }

    return (
        <div className="container mx-auto max-w-5xl py-8 px-4 h-full overflow-y-auto">
            <div className="flex flex-col gap-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2">Knowledge Base</h1>
                    <p className="text-muted-foreground">
                        Upload documents to provide custom context for the AI agent.
                    </p>
                </div>

                <FileUploadZone
                    onUploadStart={() => setLocalError(null)}
                    onUploadSuccess={() => {
                        // Realtime subscription handles list updates
                    }}
                    onUploadError={(err) => setLocalError(err)}
                />

                {error && (
                    <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive">
                        {error}
                    </div>
                )}

                <div className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
                    <div className="p-6 pb-4 border-b">
                        <h3 className="font-semibold leading-none tracking-tight">Uploaded Documents</h3>
                    </div>

                    <div className="p-0">
                        {isLoading ? (
                            <div className="flex justify-center p-8">
                                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                            </div>
                        ) : documents.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-12 text-center">
                                <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
                                <h3 className="text-lg font-medium">No documents yet</h3>
                                <p className="text-sm text-muted-foreground max-w-sm mt-1">
                                    Upload a document above to add it to the agent's knowledge base.
                                </p>
                            </div>
                        ) : (
                            <div className="relative w-full overflow-auto">
                                <table className="w-full caption-bottom text-sm">
                                    <thead className="[&_tr]:border-b bg-muted/50">
                                        <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Name</th>
                                            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Size</th>
                                            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                                            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Uploaded</th>
                                            <th className="h-10 px-4 align-middle font-medium text-muted-foreground w-[50px]"></th>
                                        </tr>
                                    </thead>
                                    <tbody className="[&_tr:last-child]:border-0">
                                        {documents.map((doc) => (
                                            <tr key={doc.id} className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted group">
                                                <td className="p-4 align-middle">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="h-4 w-4 text-muted-foreground" />
                                                        <span className="font-medium truncate max-w-[300px]" title={doc.filename}>
                                                            {doc.filename}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="p-4 align-middle text-muted-foreground">
                                                    {formatBytes(doc.file_size)}
                                                </td>
                                                <td className="p-4 align-middle">
                                                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${getStatusColor(doc.status)}`}>
                                                        {doc.status}
                                                    </span>
                                                    {doc.error_message && (
                                                        <p className="text-xs text-destructive mt-1 max-w-[200px] truncate" title={doc.error_message}>
                                                            {doc.error_message}
                                                        </p>
                                                    )}
                                                </td>
                                                <td className="p-4 align-middle text-muted-foreground text-xs">
                                                    {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
                                                </td>
                                                <td className="p-4 align-middle">
                                                    <button
                                                        onClick={() => handleDelete(doc.id)}
                                                        className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-destructive hover:text-destructive-foreground h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100"
                                                        title="Delete document"
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
