import { useState } from 'react'
import { UploadCloud, Loader2 } from 'lucide-react'
import { supabase } from '@/lib/supabase'

interface FileUploadZoneProps {
    onUploadStart: () => void
    onUploadSuccess: () => void
    onUploadError: (error: string) => void
}

const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/markdown',
    'text/plain',
    'text/html'
]
const MAX_SIZE = 50 * 1024 * 1024 // 50MB

export default function FileUploadZone({ onUploadStart, onUploadSuccess, onUploadError }: FileUploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        const files = Array.from(e.dataTransfer.files)
        await handleFiles(files)
    }

    const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.length) {
            await handleFiles(Array.from(e.target.files))
        }
        // Clear input so we can select the same file again if needed
        e.target.value = ''
    }

    const handleFiles = async (files: globalThis.File[]) => {
        if (files.length === 0) return

        // Take the first file for now (simple one-at-a-time upload)
        const file = files[0]

        // Validate size
        if (file.size > MAX_SIZE) {
            onUploadError(`File ${file.name} is too large. Max size is 50MB.`)
            return
        }

        // Validate type loosely by extension (relying on backend for strict check)
        const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
        const allowedExtensions = ['.pdf', '.docx', '.md', '.txt', '.html']
        if (!allowedExtensions.includes(ext) && !ALLOWED_TYPES.includes(file.type)) {
            onUploadError(`File type not supported for ${file.name}. Allowed: PDF, DOCX, MD, TXT, HTML`)
            return
        }

        setIsUploading(true)
        onUploadStart()

        try {
            const { data: { session } } = await supabase.auth.getSession()
            if (!session) throw new Error('Not authenticated')

            const formData = new FormData()
            formData.append('file', file)

            const response = await fetch('http://localhost:8000/api/documents/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`,
                },
                body: formData,
            })

            if (!response.ok) {
                const err = await response.json()
                throw new Error(err.detail || 'Upload failed')
            }

            onUploadSuccess()
        } catch (err: any) {
            onUploadError(err.message)
        } finally {
            setIsUploading(false)
        }
    }

    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative rounded-xl border-2 border-dashed p-10 transition-colors flex flex-col items-center justify-center text-center ${isDragging
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-muted-foreground/50 hover:bg-muted/50'
                }`}
        >
            <input
                type="file"
                id="file-upload"
                className="hidden"
                onChange={handleFileInput}
                accept=".pdf,.docx,.txt,.md,.html"
                disabled={isUploading}
            />

            <div className="rounded-full bg-primary/10 p-4 mb-4">
                {isUploading ? (
                    <Loader2 className="h-8 w-8 text-primary animate-spin" />
                ) : (
                    <UploadCloud className="h-8 w-8 text-primary" />
                )}
            </div>

            <h3 className="text-lg font-semibold tracking-tight mb-1">
                {isUploading ? 'Uploading...' : 'Drop your document here'}
            </h3>

            <p className="text-sm text-muted-foreground mb-4 max-w-sm">
                {isUploading
                    ? 'Please wait while we securely upload your file.'
                    : 'Supported formats: PDF, DOCX, TXT, MD, HTML. Max file size: 50MB.'}
            </p>

            {!isUploading && (
                <label
                    htmlFor="file-upload"
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 cursor-pointer"
                >
                    Browse Files
                </label>
            )}
        </div>
    )
}
