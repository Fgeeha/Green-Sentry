import React, { useState } from 'react'
import ImageUpload from './components/ImageUpload'
import ContextForm from './components/ContextForm'
import DiagnosisResult from './components/DiagnosisResult'
import LoadingSpinner from './components/LoadingSpinner'
import { diagnosePlant } from './services/api'
import { Leaf, Brain, FlaskConical } from 'lucide-react'

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

  const handleDiagnose = async () => {
    if (!image) {
      setError('Пожалуйста, загрузите изображение')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await diagnosePlant(image, context)
      setResult(response)
    } catch (err) {
      setError(err.message || 'Произошла ошибка при диагностике')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-green-600 text-white py-4 text-center text-xl font-semibold shadow-md">
        🌿 Plant Disease Reasoning — Интеллектуальная диагностика (AI + GigaChat)
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column - Input */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Leaf size={20} /> 1. Загрузите изображение
          </h2>
          <ImageUpload image={image} setImage={setImage} />

          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Brain size={20} /> 2. Контекст выращивания
          </h2>
          <ContextForm context={context} setContext={setContext} />

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

        {/* Right Column - Results */}
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
      </main>

      {/* Footer */}
      <footer className="text-center text-sm text-gray-500 py-4 border-t">
        © 2025 Plant Disease Reasoning Pipeline • Powered by GigaChat & PyTorch
      </footer>
    </div>
  )
}

export default App
