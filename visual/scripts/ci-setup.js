#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Setting up CI environment...');

// Check if we're in the visual directory
const packageJsonPath = path.join(process.cwd(), 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('❌ Please run this script from the visual directory');
  process.exit(1);
}

try {
  // Clean install with legacy peer deps
  console.log('📦 Installing dependencies with legacy peer deps...');
  execSync('npm ci --legacy-peer-deps', { stdio: 'inherit' });
  
  // Install Playwright browsers
  console.log('🌐 Installing Playwright browsers...');
  execSync('npx playwright install --with-deps', { stdio: 'inherit' });
  
  // Create test-results directory
  const testResultsDir = path.join(process.cwd(), 'test-results');
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
    console.log('📁 Created test-results directory');
  }
  
  console.log('✅ CI setup complete!');
  
} catch (error) {
  console.error('❌ CI setup failed:', error.message);
  process.exit(1);
} 