import React, { useEffect, useState } from 'react'
import ImageUpload from './components/ImageUpload'
import ContextForm from './components/ContextForm'
import DiagnosisResult from './components/DiagnosisResult'
import DiagnosisHistory from './components/DiagnosisHistory'
import LoadingSpinner from './components/LoadingSpinner'
import { diagnosePlant } from './services/api'
import { Leaf, Brain, FlaskConical } from 'lucide-react'

const HISTORY_STORAGE_KEY = 'diagnosisHistory'
const HISTORY_LIMIT = 10

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    if (!file || typeof window === 'undefined' || typeof FileReader === 'undefined') {
      resolve(null)
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      resolve(reader.result)
    }
    reader.onerror = () => {
      reject(reader.error)
    }
    reader.readAsDataURL(file)
  })

const loadHistory = () => {
  if (typeof window === 'undefined') {
    return []
  }

  try {
    const stored = window.localStorage.getItem(HISTORY_STORAGE_KEY)
    if (!stored) {
      return []
    }

    const parsed = JSON.parse(stored)
    if (Array.isArray(parsed)) {
      return parsed
    }

    return []
  } catch (error) {
    console.warn('Не удалось загрузить историю запросов:', error)
    return []
  }
}

function App() {
  const [image, setImage] = useState(null)
  const [context, setContext] = useState({
    region: 'Москва',
    climate: 'умеренно-континентальный',
    plant_age: '',
    additional_context: '',
    use_reasoning: true,
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState(loadHistory)

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    try {
      window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history))
    } catch (storageError) {
      console.warn('Не удалось сохранить историю запросов:', storageError)
    }
  }, [history])

  const handleDiagnose = async () => {
    if (!image) {
      setError('Пожалуйста, загрузите изображение')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const [response, imagePreview] = await Promise.all([
        diagnosePlant(image, context),
        readFileAsDataUrl(image).catch(() => null),
      ])
      setResult(response)

        const newEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        disease: response?.cv_result?.disease_name,
        confidence: response?.cv_result?.confidence,
        pipelineVersion: response?.pipeline_version,
        report: response?.report,
        region: context.region,
        useReasoning: context.use_reasoning,
        imagePreview,
        imageName: image?.name,
      }

      setHistory((prevHistory) => {
        const updatedHistory = [newEntry, ...prevHistory]
        if (updatedHistory.length > HISTORY_LIMIT) {
          return updatedHistory.slice(0, HISTORY_LIMIT)
        }
        return updatedHistory
      })
    } catch (err) {
      setError(err.message || 'Произошла ошибка при диагностике')
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = () => {
    setHistory([])
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-green-600 text-white py-4 text-center text-xl font-semibold shadow-md">
        🌿 Green Sentry — Интеллектуальная диагностика (CV + GigaChat)
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column - Input */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Leaf size={20} /> 1. Загрузите изображение
          </h2>
          <ImageUpload selectedImage={image} onImageSelect={setImage} />

          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Brain size={20} /> 2. Контекст выращивания
          </h2>
          <ContextForm context={context} onChange={setContext} />

          <button
            onClick={handleDiagnose}
            disabled={loading}
            className="w-full py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
          >
            {loading ? 'Анализируем...' : '🔬 Начать диагностику'}
          </button>

          {error && (
            <div className="text-red-600 bg-red-100 p-2 rounded-md">{error}</div>
          )}
        </div>

        {/* Right Column - Results & History */}
        <div className="space-y-4">
          <div className="p-4 border rounded-md bg-white shadow-sm">
            {loading && <LoadingSpinner />}
            {result && !loading && <DiagnosisResult result={result} />}
            {!result && !loading && (
              <div className="text-center text-gray-500">
                <FlaskConical className="mx-auto mb-2" size={32} />
                <p className="font-medium">Готов к анализу</p>
                <p>Загрузите изображение растения и нажмите "Начать диагностику"</p>
              </div>
            )}
          </div>

          <DiagnosisHistory history={history} onClear={handleClearHistory} />
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center text-sm text-gray-500 py-4 border-t">
        © {new Date().getFullYear()} Green Sentry Pipeline
      </footer>
    </div>
  )
}

export default App
