import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon } from 'lucide-react'

const ImageUpload = ({ onImageSelect, selectedImage }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles && acceptedFiles.length > 0) {
        onImageSelect(acceptedFiles[0])
      }
    },
    [onImageSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
    multiple: false,
  })

  const clearImage = (e) => {
    e.stopPropagation()
    onImageSelect(null)
  }

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
        isDragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-green-400'
      }`}
    >
      <input {...getInputProps()} />

      {/* Нет выбранного изображения */}
      {!selectedImage ? (
        <div className="flex flex-col items-center justify-center space-y-2 text-gray-600">
          <Upload className="w-8 h-8 text-green-600" />
          {isDragActive ? (
            <p className="font-medium text-green-700">Отпустите файл здесь...</p>
          ) : (
            <>
              <p className="font-medium">Перетащите изображение или нажмите для выбора</p>
              <p className="text-sm text-gray-400">
                Поддерживаются форматы: JPG, PNG (макс. 10 MB)
              </p>
            </>
          )}
        </div>
      ) : (
        /* Изображение выбрано */
        <div className="relative flex flex-col items-center space-y-3">
          <ImageIcon className="w-10 h-10 text-green-600" />
          <p className="text-sm text-gray-700 font-medium">
            {selectedImage.name} ({(selectedImage.size / 1024 / 1024).toFixed(2)} MB)
          </p>

          {/* Кнопка очистки */}
          <button
            onClick={clearImage}
            className="absolute top-0 right-0 p-1 text-gray-500 hover:text-red-600"
            title="Удалить изображение"
          >
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  )
}

export default ImageUpload
