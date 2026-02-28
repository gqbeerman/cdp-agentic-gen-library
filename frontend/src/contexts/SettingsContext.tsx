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

const DEFAULT_LLM_MODEL = 'gpt-4o'
const DEFAULT_EMBEDDING_MODEL = 'text-embedding-3-small'

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children }: { children: ReactNode }) {
    const [llmModel, setLlmModel] = useState<string>(() => {
        return localStorage.getItem('llm_model') || DEFAULT_LLM_MODEL
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
