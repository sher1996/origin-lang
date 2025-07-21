import { useState, useCallback } from 'react';

export interface Connection {
  id: string;
  fromBlockId: string;
  fromOutputId: string;
  toBlockId: string;
  toInputId: string;
}

export function useConnections() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [draggingConnection, setDraggingConnection] = useState<{
    fromBlockId: string;
    fromOutputId: string;
    position: { x: number; y: number };
  } | null>(null);

  const addConnection = useCallback((connection: Omit<Connection, 'id'>) => {
    const newConnection: Connection = {
      ...connection,
      id: `conn-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
    setConnections(prev => [...prev, newConnection]);
  }, []);

  const removeConnection = useCallback((connectionId: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== connectionId));
  }, []);

  const startDraggingConnection = useCallback((
    fromBlockId: string,
    fromOutputId: string,
    position: { x: number; y: number }
  ) => {
    setDraggingConnection({ fromBlockId, fromOutputId, position });
  }, []);

  const stopDraggingConnection = useCallback(() => {
    setDraggingConnection(null);
  }, []);

  const updateDraggingPosition = useCallback((position: { x: number; y: number }) => {
    if (draggingConnection) {
      setDraggingConnection(prev => prev ? { ...prev, position } : null);
    }
  }, [draggingConnection]);

  const canConnect = useCallback((
    fromBlockId: string,
    fromOutputId: string,
    toBlockId: string,
    toInputId: string
  ) => {
    // Don't connect to self
    if (fromBlockId === toBlockId) return false;
    
    // Don't create duplicate connections
    const existingConnection = connections.find(conn => 
      conn.fromBlockId === fromBlockId && 
      conn.fromOutputId === fromOutputId &&
      conn.toBlockId === toBlockId && 
      conn.toInputId === toInputId
    );
    
    if (existingConnection) return false;
    
    return true;
  }, [connections]);

  return {
    connections,
    setConnections,
    draggingConnection,
    addConnection,
    removeConnection,
    startDraggingConnection,
    stopDraggingConnection,
    updateDraggingPosition,
    canConnect,
  };
} 