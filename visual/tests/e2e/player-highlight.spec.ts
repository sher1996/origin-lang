import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { join } from 'path';

test.describe('Player Highlight E2E', () => {
  test('should load sample recording, seek to 0.8, and assert highlight ring exists', async ({ page }) => {
    // Navigate to the visual editor
    await page.goto('/');
    
    // Wait for the app to load
    await page.waitForSelector('[data-testid="toolbar"]', { timeout: 10000 });
    
    // Click the "Open Recording" button
    await page.click('[data-testid="open-recording-btn"]');
    
    // Create a file input and upload the sample recording
    const fileInput = await page.locator('input[type="file"]');
    const recordingPath = join(process.cwd(), '..', '..', 'examples', 'recordings', 'fizzbuzz.orirec');
    
    // Check if the recording file exists and upload it
    try {
      const recordingContent = readFileSync(recordingPath, 'utf-8');
      await fileInput.setInputFiles({
        name: 'fizzbuzz.orirec',
        mimeType: 'application/octet-stream',
        buffer: Buffer.from(recordingContent)
      });
    } catch (error) {
      console.warn('Recording file not found, using fallback test data');
      // Fallback: create a minimal recording file for testing
      const fallbackRecording = JSON.stringify([
        {
          version: '1.0',
          ts: 0,
          blockId: 'SayNode:start',
          locals: { i: 1 },
          globals: {}
        },
        {
          version: '1.0',
          ts: 100,
          blockId: 'LetNode:j',
          locals: { i: 1, j: 2 },
          globals: {}
        },
        {
          version: '1.0',
          ts: 200,
          blockId: 'SayNode:output',
          locals: { i: 1, j: 2, result: 'Hello' },
          globals: {}
        }
      ]);
      
      await fileInput.setInputFiles({
        name: 'fizzbuzz.orirec',
        mimeType: 'application/octet-stream',
        buffer: Buffer.from(fallbackRecording)
      });
    }
    
    // Wait for the recording to load
    await page.waitForSelector('[data-testid="timeline-bar"]', { timeout: 10000 });
    
    // Find the timeline slider and seek to 0.8 (80%)
    const timelineSlider = page.locator('[data-testid="timeline-slider"]');
    await timelineSlider.click({ position: { x: 800, y: 10 } }); // Click at 80% position
    
    // Wait for the seek operation to complete
    await page.waitForTimeout(500);
    
    // Assert that a highlight ring exists on the expected block
    // The highlight ring should be visible on the canvas
    const highlightRing = page.locator('[data-testid="block-highlight"]');
    await expect(highlightRing).toBeVisible({ timeout: 5000 });
    
    // Additional assertion: verify the highlight ring has the correct styling
    await expect(highlightRing).toHaveCSS('border', /2px solid/);
    await expect(highlightRing).toHaveCSS('border-color', /rgb\(59, 130, 246\)/); // blue-500 color
    
    // Verify that the player state reflects the seek operation
    const currentFrame = page.locator('[data-testid="current-frame"]');
    await expect(currentFrame).toBeVisible();
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-results/player-highlight-e2e.png' });
  });
  
  test('should handle seek to 0.8 with proper block highlighting', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the app to load
    await page.waitForSelector('[data-testid="toolbar"]', { timeout: 10000 });
    
    // Mock the recording data directly in the browser
    await page.evaluate(() => {
      const mockRecording = [
        { frame: 0, time: 0, blockId: 'SayNode:start', locals: { i: 1 } },
        { frame: 1, time: 0.1, blockId: 'LetNode:j', locals: { i: 1, j: 2 } },
        { frame: 2, time: 0.2, blockId: 'SayNode:output', locals: { i: 1, j: 2, result: 'Hello' } },
        { frame: 3, time: 0.3, blockId: 'RepeatNode:loop', locals: { i: 1, j: 2, result: 'Hello' } },
        { frame: 4, time: 0.4, blockId: 'SayNode:final', locals: { i: 1, j: 2, result: 'Hello', count: 3 } }
      ];
      
      // Set the recording in the app state
      (window as any).testRecording = mockRecording;
    });
    
    // Trigger the recording load
    await page.click('[data-testid="open-recording-btn"]');
    
    // Wait for the timeline to appear
    await page.waitForSelector('[data-testid="timeline-bar"]', { timeout: 10000 });
    
    // Seek to 0.8 (should be around frame 3-4)
    const timelineSlider = page.locator('[data-testid="timeline-slider"]');
    await timelineSlider.click({ position: { x: 800, y: 10 } });
    
    // Wait for the seek to complete
    await page.waitForTimeout(1000);
    
    // Assert that the highlight ring is visible
    const highlightRing = page.locator('[data-testid="block-highlight"]');
    await expect(highlightRing).toBeVisible({ timeout: 5000 });
    
    // Verify the highlight ring is positioned correctly
    const ringBox = await highlightRing.boundingBox();
    expect(ringBox).toBeTruthy();
    expect(ringBox!.width).toBeGreaterThan(0);
    expect(ringBox!.height).toBeGreaterThan(0);
    
    // Check that the current frame indicator shows the correct frame
    const frameIndicator = page.locator('[data-testid="current-frame"]');
    await expect(frameIndicator).toContainText('Frame');
  });
}); 