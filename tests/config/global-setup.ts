// Global setup for Playwright E2E tests
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global E2E test setup...');
  
  // Launch browser for setup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Check if the application is accessible
    const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';
    console.log(`🌐 Checking application availability at ${baseURL}`);
    
    await page.goto(baseURL, { waitUntil: 'networkidle' });
    
    // Verify the application loads correctly
    await page.waitForSelector('body', { timeout: 30000 });
    console.log('✅ Application is accessible');
    
    // Setup test data if needed
    await setupTestData(page);
    
    // Perform any authentication setup if needed
    await setupAuthentication(page);
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
}

async function setupTestData(page: any) {
  console.log('📊 Setting up test data...');
  
  // In a real application, you might:
  // - Seed the database with test data
  // - Clear existing test data
  // - Setup specific test scenarios
  
  // For now, we'll just verify we can access the API
  try {
    const response = await page.evaluate(async () => {
      const res = await fetch('/api/health', { method: 'GET' });
      return res.ok;
    });
    
    if (response) {
      console.log('✅ API health check passed');
    } else {
      console.log('⚠️  API health check failed, but continuing...');
    }
  } catch (error) {
    console.log('⚠️  Could not perform API health check:', error.message);
  }
}

async function setupAuthentication(page: any) {
  console.log('🔐 Setting up authentication...');
  
  // In a real application with authentication, you might:
  // - Create test user accounts
  // - Generate authentication tokens
  // - Setup different user roles for testing
  
  // For the current implementation without auth, we'll skip this
  console.log('⏭️  No authentication setup required');
}

export default globalSetup; 