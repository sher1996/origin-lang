import { useEffect, useRef } from 'react';
import type { BlockInstance } from '../blocks/definitions';
import type { Connection } from './useConnections';



interface AutosaveData {
  blocks: BlockInstance[];
  connections: Connection[];
  timestamp: number;
}

const AUTOSAVE_KEY = 'origin:lastProject';
const AUTOSAVE_INTERVAL = 10000; // 10 seconds

export function useAutosave(
  blocks: BlockInstance[],
  connections: Connection[],
  onRestore?: (data: AutosaveData) => void
) {
  const lastSaveRef = useRef<AutosaveData | null>(null);
  const intervalRef = useRef<number | null>(null);

  // Save function
  const saveToStorage = () => {
    const data: AutosaveData = {
      blocks,
      connections,
      timestamp: Date.now()
    };
    
    try {
      localStorage.setItem(AUTOSAVE_KEY, JSON.stringify(data));
      lastSaveRef.current = data;
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  };

  // Load function
  const loadFromStorage = (): AutosaveData | null => {
    try {
      const stored = localStorage.getItem(AUTOSAVE_KEY);
      if (!stored) return null;
      
      const data = JSON.parse(stored) as AutosaveData;
      
      // Check if data is recent (within last hour)
      const oneHourAgo = Date.now() - (60 * 60 * 1000);
      if (data.timestamp < oneHourAgo) {
        localStorage.removeItem(AUTOSAVE_KEY);
        return null;
      }
      
      return data;
    } catch (error) {
      console.warn('Failed to load from localStorage:', error);
      return null;
    }
  };

  // Check for existing session on mount
  useEffect(() => {
    const savedData = loadFromStorage();
    if (savedData && onRestore) {
      const shouldRestore = window.confirm(
        'Found a previous session. Would you like to restore it?'
      );
      if (shouldRestore) {
        onRestore(savedData);
      } else {
        localStorage.removeItem(AUTOSAVE_KEY);
      }
    }
  }, [onRestore]);

  // Set up auto-save interval
  useEffect(() => {
    intervalRef.current = setInterval(saveToStorage, AUTOSAVE_INTERVAL) as any;
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [blocks, connections]);

  // Save on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      saveToStorage();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [blocks, connections]);

  return {
    saveToStorage,
    loadFromStorage,
    hasSavedData: () => loadFromStorage() !== null
  };
} 