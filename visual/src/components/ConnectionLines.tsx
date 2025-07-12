import React from 'react';
import type { Connection } from '../hooks/useConnections';
import type { BlockInstance } from '../blocks/definitions';

interface ConnectionLinesProps {
  connections: Connection[];
  blocks: BlockInstance[];
  draggingConnection?: {
    fromBlockId: string;
    fromOutputId: string;
    position: { x: number; y: number };
  } | null;
}

const ConnectionLines: React.FC<ConnectionLinesProps> = ({ 
  connections, 
  blocks, 
  draggingConnection 
}) => {
  const getBlockPosition = (blockId: string) => {
    const block = blocks.find(b => b.id === blockId);
    return block?.position || { x: 0, y: 0 };
  };

  const getConnectionPath = (
    fromPos: { x: number; y: number },
    toPos: { x: number; y: number }
  ) => {
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    
    // Create a curved path using quadratic bezier
    const controlPoint1 = {
      x: fromPos.x + dx * 0.5,
      y: fromPos.y
    };
    const controlPoint2 = {
      x: toPos.x - dx * 0.5,
      y: toPos.y
    };
    
    return `M ${fromPos.x} ${fromPos.y} Q ${controlPoint1.x} ${controlPoint1.y} ${toPos.x} ${toPos.y}`;
  };

  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{ width: '100%', height: '100%' }}
    >
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#3b82f6"
          />
        </marker>
      </defs>
      
      {/* Render existing connections */}
      {connections.map(connection => {
        const fromBlock = blocks.find(b => b.id === connection.fromBlockId);
        const toBlock = blocks.find(b => b.id === connection.toBlockId);
        
        if (!fromBlock || !toBlock) return null;
        
        const fromPos = {
          x: fromBlock.position.x + 150, // Approximate output position
          y: fromBlock.position.y + 30
        };
        const toPos = {
          x: toBlock.position.x, // Approximate input position
          y: toBlock.position.y + 30
        };
        
        return (
          <path
            key={connection.id}
            d={getConnectionPath(fromPos, toPos)}
            stroke="#3b82f6"
            strokeWidth="2"
            fill="none"
            markerEnd="url(#arrowhead)"
          />
        );
      })}
      
      {/* Render dragging connection */}
      {draggingConnection && (
        <path
          d={getConnectionPath(
            { x: draggingConnection.position.x, y: draggingConnection.position.y },
            { x: draggingConnection.position.x + 50, y: draggingConnection.position.y }
          )}
          stroke="#3b82f6"
          strokeWidth="2"
          strokeDasharray="5,5"
          fill="none"
          opacity="0.7"
        />
      )}
    </svg>
  );
};

export default ConnectionLines; 