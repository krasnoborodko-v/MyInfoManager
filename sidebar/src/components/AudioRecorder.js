import React, { useState, useRef, useCallback } from 'react';
import { Mic, Square, Circle, Trash2 } from 'lucide-react';

/**
 * Компонент записи аудио с микрофона.
 * @param {Object} props
 * @param {Function} props.onRecordingComplete - Callback с записанным аудио (Blob)
 * @param {Function} props.onCancel - Callback при отмене
 */
function AudioRecorder({ onRecordingComplete, onCancel }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState(null);
  const [permission, setPermission] = useState(null); // null, 'granted', 'denied'
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  // Запрос доступа к микрофону
  const requestMicrophonePermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      streamRef.current = stream;
      setPermission('granted');
      return true;
    } catch (err) {
      console.error('Ошибка доступа к микрофону:', err);
      setPermission('denied');
      setError('Нет доступа к микрофону. Проверьте разрешения браузера.');
      return false;
    }
  }, []);

  // Начало записи
  const startRecording = useCallback(async () => {
    setError(null);
    
    // Проверяем поддержку API
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError('Ваш браузер не поддерживает запись аудио');
      return;
    }

    // Запрашиваем доступ если ещё не получен
    if (permission !== 'granted') {
      const hasPermission = await requestMicrophonePermission();
      if (!hasPermission) return;
    }

    try {
      // Создаем MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/mp4';

      mediaRecorderRef.current = new MediaRecorder(streamRef.current, {
        mimeType,
        audioBitsPerSecond: 128000
      });

      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorderRef.current.mimeType 
        });
        
        // Конвертируем в MP3 для совместимости (опционально)
        const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, {
          type: audioBlob.type
        });
        
        onRecordingComplete(audioFile);
        
        // Очищаем
        audioChunksRef.current = [];
      };

      // Запускаем запись
      mediaRecorderRef.current.start(100); // Собираем данные каждые 100мс
      setIsRecording(true);
      setRecordingTime(0);

      // Таймер
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Ошибка при начале записи:', err);
      setError('Ошибка при начале записи');
    }
  }, [permission, requestMicrophonePermission, onRecordingComplete]);

  // Остановка записи
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording]);

  // Отмена записи
  const cancelRecording = useCallback(() => {
    stopRecording();
    
    // Освобождаем микрофон
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    setRecordingTime(0);
    setError(null);
    onCancel();
  }, [stopRecording, onCancel]);

  // Форматирование времени
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Очистка при размонтировании
  React.useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="audio-recorder">
      <div className="recorder-controls">
        {!isRecording ? (
          <>
            <button 
              className="record-btn" 
              onClick={startRecording}
              disabled={permission === 'denied'}
            >
              <Circle size={20} className="record-icon" />
              Начать запись
            </button>
            <button className="cancel-btn" onClick={cancelRecording}>
              <Trash2 size={16} />
            </button>
          </>
        ) : (
          <>
            <div className="recording-timer">{formatTime(recordingTime)}</div>
            <div className="recording-indicator">
              <span className="pulse"></span>
              Запись...
            </div>
            <button className="stop-btn" onClick={stopRecording}>
              <Square size={20} />
              Стоп
            </button>
          </>
        )}
      </div>
      
      {error && (
        <div className="recorder-error">{error}</div>
      )}
      
      {permission === 'denied' && (
        <div className="permission-denied">
          Разрешите доступ к микрофону в настройках браузера
        </div>
      )}
    </div>
  );
}

export default AudioRecorder;
