import { createContext, useContext, useState, type ReactNode } from 'react'

interface SettingsContextType {
    llmModel: string
    embeddingModel: string
    openRouterKey: string
    openaiKey: string
    googleKey: string
    xaiKey: string
    customModels: string[]
    updateSettings: (settings: Partial<Omit<SettingsContextType, 'updateSettings'>>) => void
}

const DEFAULT_LLM_MODEL = 'openai/gpt-4o'
const DEFAULT_EMBEDDING_MODEL = 'qwen/qwen3-embedding-8b'

// Migrate old unprefixed model names to OpenRouter-compatible names
const MODEL_MIGRATION: Record<string, string> = {
    'gpt-4o': 'openai/gpt-4o',
    'gpt-4-turbo': 'openai/gpt-4-turbo',
    'claude-3-opus-20240229': 'anthropic/claude-3-opus-20240229',
    'claude-3-5-sonnet-20240620': 'anthropic/claude-3.5-sonnet',
    'gemini-1.5-pro': 'google/gemini-2.0-flash-001',
}

function migrateModel(stored: string | null, defaultModel: string): string {
    if (!stored) return defaultModel
    return MODEL_MIGRATION[stored] || stored
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children }: { children: ReactNode }) {
    const [llmModel, setLlmModel] = useState<string>(() => {
        const stored = localStorage.getItem('llm_model')
        const migrated = migrateModel(stored, DEFAULT_LLM_MODEL)
        if (stored && migrated !== stored) localStorage.setItem('llm_model', migrated)
        return migrated
    })

    const [embeddingModel, setEmbeddingModel] = useState<string>(() => {
        return localStorage.getItem('embedding_model') || DEFAULT_EMBEDDING_MODEL
    })

    const [openRouterKey, setOpenRouterKey] = useState<string>(() => {
        return localStorage.getItem('openrouter_key') || ''
    })

    const [openaiKey, setOpenaiKey] = useState<string>(() => {
        return localStorage.getItem('openai_key') || ''
    })

    const [googleKey, setGoogleKey] = useState<string>(() => {
        return localStorage.getItem('google_key') || ''
    })

    const [xaiKey, setXaiKey] = useState<string>(() => {
        return localStorage.getItem('xai_key') || ''
    })

    const [customModels, setCustomModels] = useState<string[]>(() => {
        try {
            const stored = localStorage.getItem('custom_models')
            if (!stored) return []
            const parsed = JSON.parse(stored)
            return Array.isArray(parsed) ? parsed : []
        } catch {
            return []
        }
    })

    const updateSettings = (settings: Partial<Omit<SettingsContextType, 'updateSettings'>>) => {
        if (settings.llmModel !== undefined) {
            setLlmModel(settings.llmModel)
            localStorage.setItem('llm_model', settings.llmModel)
        }
        if (settings.embeddingModel !== undefined) {
            setEmbeddingModel(settings.embeddingModel)
            localStorage.setItem('embedding_model', settings.embeddingModel)
        }
        if (settings.openRouterKey !== undefined) {
            setOpenRouterKey(settings.openRouterKey)
            localStorage.setItem('openrouter_key', settings.openRouterKey)
        }
        if (settings.openaiKey !== undefined) {
            setOpenaiKey(settings.openaiKey)
            localStorage.setItem('openai_key', settings.openaiKey)
        }
        if (settings.googleKey !== undefined) {
            setGoogleKey(settings.googleKey)
            localStorage.setItem('google_key', settings.googleKey)
        }
        if (settings.xaiKey !== undefined) {
            setXaiKey(settings.xaiKey)
            localStorage.setItem('xai_key', settings.xaiKey)
        }
        if (settings.customModels !== undefined) {
            setCustomModels(settings.customModels)
            localStorage.setItem('custom_models', JSON.stringify(settings.customModels))
        }
    }

    return (
        <SettingsContext.Provider value={{
            llmModel,
            embeddingModel,
            openRouterKey,
            openaiKey,
            googleKey,
            xaiKey,
            customModels,
            updateSettings
        }}>
            {children}
        </SettingsContext.Provider>
    )
}

export function useSettings() {
    const context = useContext(SettingsContext)
    if (context === undefined) {
        throw new Error('useSettings must be used within a SettingsProvider')
    }
    return context
}
