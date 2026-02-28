import { useState, useEffect } from 'react'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { useSettings } from '@/contexts/SettingsContext'
import { Plus } from 'lucide-react'

interface SettingsModalProps {
    isOpen: boolean
    onClose: () => void
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const settings = useSettings()

    // Local state for all settings
    const [localLlmModel, setLocalLlmModel] = useState(settings.llmModel)
    const [localEmbeddingModel, setLocalEmbeddingModel] = useState(settings.embeddingModel)
    const [localOpenRouterKey, setLocalOpenRouterKey] = useState(settings.openRouterKey)
    const [localOpenaiKey, setLocalOpenaiKey] = useState(settings.openaiKey)
    const [localGoogleKey, setLocalGoogleKey] = useState(settings.googleKey)
    const [localXaiKey, setLocalXaiKey] = useState(settings.xaiKey)
    const [localCustomModels, setLocalCustomModels] = useState(settings.customModels)

    const [newModelInput, setNewModelInput] = useState('')
    const [activeKeyProvider, setActiveKeyProvider] = useState<'openai' | 'google' | 'xai' | 'openrouter'>('openai')

    // Reset local state when modal opens
    useEffect(() => {
        if (isOpen) {
            setLocalLlmModel(settings.llmModel)
            setLocalEmbeddingModel(settings.embeddingModel)
            setLocalOpenRouterKey(settings.openRouterKey)
            setLocalOpenaiKey(settings.openaiKey)
            setLocalGoogleKey(settings.googleKey)
            setLocalXaiKey(settings.xaiKey)
            setLocalCustomModels(settings.customModels)
        }
    }, [isOpen, settings])

    const handleSave = () => {
        settings.updateSettings({
            llmModel: localLlmModel,
            embeddingModel: localEmbeddingModel,
            openRouterKey: localOpenRouterKey,
            openaiKey: localOpenaiKey,
            googleKey: localGoogleKey,
            xaiKey: localXaiKey,
            customModels: localCustomModels,
        })
        onClose()
    }

    const handleAddCustomModel = () => {
        if (newModelInput.trim() && !localCustomModels.includes(newModelInput.trim())) {
            const updated = [...localCustomModels, newModelInput.trim()]
            setLocalCustomModels(updated)
            setLocalLlmModel(newModelInput.trim()) // auto-select the newly added model
            setNewModelInput('')
        }
    }

    const getKeyPlaceholder = () => {
        switch (activeKeyProvider) {
            case 'openai': return 'sk-...'
            case 'google': return 'AIza...'
            case 'xai': return 'xai-...'
            case 'openrouter': return 'sk-or-v1-...'
            default: return 'Enter API Key'
        }
    }

    const getKeyValue = () => {
        switch (activeKeyProvider) {
            case 'openai': return localOpenaiKey
            case 'google': return localGoogleKey
            case 'xai': return localXaiKey
            case 'openrouter': return localOpenRouterKey
            default: return ''
        }
    }

    const handleKeyChange = (val: string) => {
        switch (activeKeyProvider) {
            case 'openai': setLocalOpenaiKey(val); break
            case 'google': setLocalGoogleKey(val); break
            case 'xai': setLocalXaiKey(val); break
            case 'openrouter': setLocalOpenRouterKey(val); break
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-[500px] p-0 overflow-hidden flex flex-col max-h-[90vh]">
                <DialogHeader className="p-6 pb-0">
                    <DialogTitle>Settings</DialogTitle>
                    <DialogDescription>
                        Configure the AI models used for chat and document ingestion.
                    </DialogDescription>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto p-6 pt-4">
                    <div className="grid gap-6">
                        <div className="grid gap-3">
                            <Label htmlFor="llm-model">Chat Model</Label>
                            <Select value={localLlmModel} onValueChange={setLocalLlmModel}>
                                <SelectTrigger id="llm-model">
                                    <SelectValue placeholder="Select a chat model" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px]">
                                    <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                                    <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                                    <SelectItem value="claude-3-opus-20240229">Claude 3 Opus</SelectItem>
                                    <SelectItem value="claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</SelectItem>
                                    <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                                    {localCustomModels.map((model) => (
                                        <SelectItem key={model} value={model}>
                                            {model} (Custom)
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <p className="text-[0.8rem] text-muted-foreground">
                                The model used to generate chat responses.
                            </p>
                        </div>

                        <div className="grid gap-3">
                            <Label htmlFor="embedding-model">Embedding Model</Label>
                            <Select
                                value={localEmbeddingModel}
                                onValueChange={setLocalEmbeddingModel}
                            >
                                <SelectTrigger id="embedding-model">
                                    <SelectValue placeholder="Select an embedding model" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px]">
                                    <SelectItem value="text-embedding-3-small">text-embedding-3-small</SelectItem>
                                    <SelectItem value="text-embedding-3-large">text-embedding-3-large</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-[0.8rem] text-muted-foreground">
                                The model used to vectorize uploaded documents and search queries.
                            </p>
                        </div>

                        <div className="grid gap-4 pt-4 border-t">
                            <div>
                                <h3 className="text-sm font-medium mb-1">Provider API Keys</h3>
                                <p className="text-[0.8rem] text-muted-foreground mb-3">
                                    Provide native keys for specific providers, or use OpenRouter as a fallback.
                                </p>
                            </div>

                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label className="text-xs">Select Provider</Label>
                                    <Select
                                        value={activeKeyProvider}
                                        onValueChange={(val: any) => setActiveKeyProvider(val)}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="openai">OpenAI</SelectItem>
                                            <SelectItem value="google">Google Gemini</SelectItem>
                                            <SelectItem value="xai">xAI (Grok)</SelectItem>
                                            <SelectItem value="openrouter">OpenRouter</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="grid gap-2">
                                    <Label htmlFor="provider-key" className="text-xs">
                                        {activeKeyProvider.charAt(0).toUpperCase() + activeKeyProvider.slice(1)} API Key
                                    </Label>
                                    <Input
                                        id="provider-key"
                                        type="password"
                                        placeholder={getKeyPlaceholder()}
                                        value={getKeyValue()}
                                        onChange={(e) => handleKeyChange(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="grid gap-3 pt-4 border-t">
                            <Label htmlFor="custom-model">Add Custom Model</Label>
                            <div className="flex gap-2">
                                <Input
                                    id="custom-model"
                                    placeholder="e.g. anthropic/claude-3-opus"
                                    value={newModelInput}
                                    onChange={(e) => setNewModelInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAddCustomModel()}
                                />
                                <Button type="button" variant="secondary" onClick={handleAddCustomModel}>
                                    <Plus className="h-4 w-4" />
                                </Button>
                            </div>
                            <p className="text-[0.8rem] text-muted-foreground">
                                Standard format is provider/model-name.
                            </p>
                        </div>
                    </div>
                </div>

                <DialogFooter className="p-6 pt-2 border-t flex flex-row justify-end gap-2 shrink-0">
                    <Button variant="ghost" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleSave}>
                        Save Changes
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
