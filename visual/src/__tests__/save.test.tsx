import { describe, it, expect } from 'vitest';
import type { BlockInstance } from '../blocks/definitions';
import type { Connection } from '../hooks/useConnections';

describe('Project Save/Load', () => {
  const mockBlocks: BlockInstance[] = [
    {
      id: 'test-block-1',
      definitionId: 'say',
      position: { x: 100, y: 100 },
      inputs: { expr: 'Hello World' },
      outputs: {}
    }
  ];

  const mockConnections: Connection[] = [
    {
      id: 'test-conn-1',
      fromBlockId: 'test-block-1',
      fromOutputId: 'statement',
      toBlockId: 'test-block-2',
      toInputId: 'expr'
    }
  ];

  it('should have valid block structure', () => {
    expect(mockBlocks[0]).toHaveProperty('id');
    expect(mockBlocks[0]).toHaveProperty('definitionId');
    expect(mockBlocks[0]).toHaveProperty('position');
    expect(mockBlocks[0]).toHaveProperty('inputs');
    expect(mockBlocks[0]).toHaveProperty('outputs');
  });

  it('should have valid connection structure', () => {
    expect(mockConnections[0]).toHaveProperty('id');
    expect(mockConnections[0]).toHaveProperty('fromBlockId');
    expect(mockConnections[0]).toHaveProperty('fromOutputId');
    expect(mockConnections[0]).toHaveProperty('toBlockId');
    expect(mockConnections[0]).toHaveProperty('toInputId');
  });

  it('should serialize blocks to JSON', () => {
    const json = JSON.stringify(mockBlocks);
    const parsed = JSON.parse(json);
    
    expect(parsed).toHaveLength(1);
    expect(parsed[0].id).toBe('test-block-1');
    expect(parsed[0].definitionId).toBe('say');
  });

  it('should serialize connections to JSON', () => {
    const json = JSON.stringify(mockConnections);
    const parsed = JSON.parse(json);
    
    expect(parsed).toHaveLength(1);
    expect(parsed[0].id).toBe('test-conn-1');
    expect(parsed[0].fromBlockId).toBe('test-block-1');
    expect(parsed[0].toBlockId).toBe('test-block-2');
  });
}); 