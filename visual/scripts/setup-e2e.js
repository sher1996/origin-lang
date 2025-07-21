#!/usr/bin/env node

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔧 Setting up E2E testing environment...');

// Check if we're in the visual directory
const packageJsonPath = path.join(process.cwd(), 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('❌ Please run this script from the visual directory');
  process.exit(1);
}

try {
  // Install Playwright browsers
  console.log('📦 Installing Playwright browsers...');
  execSync('npx playwright install --with-deps', { stdio: 'inherit' });
  
  // Create test-results directory
  const testResultsDir = path.join(process.cwd(), 'test-results');
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
    console.log('📁 Created test-results directory');
  }
  
  console.log('✅ E2E setup complete!');
  console.log('');
  console.log('You can now run:');
  console.log('  npm run test:e2e        # Run e2e tests');
  console.log('  npm run test:e2e:ui     # Run with UI');
  console.log('  npm run test:e2e:headed # Run in headed mode');
  
} catch (error) {
  console.error('❌ Setup failed:', error.message);
  process.exit(1);
} 