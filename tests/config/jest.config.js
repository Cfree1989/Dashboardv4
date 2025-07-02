// Jest configuration for Dashboard v4
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: '../v0',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/config/setup.ts'],
  
  // Module paths
  moduleDirectories: ['node_modules', '<rootDir>/'],
  moduleNameMapping: {
    // Handle module aliases (same as in your Next.js config)
    '^@/components/(.*)$': '<rootDir>/v0/components/$1',
    '^@/pages/(.*)$': '<rootDir>/v0/pages/$1',
    '^@/lib/(.*)$': '<rootDir>/v0/lib/$1',
    '^@/hooks/(.*)$': '<rootDir>/v0/hooks/$1',
    '^@/types/(.*)$': '<rootDir>/v0/types/$1',
    '^@/styles/(.*)$': '<rootDir>/v0/styles/$1',
    '^@/public/(.*)$': '<rootDir>/v0/public/$1',
    
    // Handle CSS imports (identity object proxy for CSS modules)
    '^.+\\.(css|sass|scss)$': 'identity-obj-proxy',
    
    // Handle image imports
    '^.+\\.(png|jpg|jpeg|gif|webp|avif|ico|bmp|svg)$': '<rootDir>/tests/__mocks__/file-mock.js',
  },
  
  // Test file patterns
  testMatch: [
    '<rootDir>/tests/**/*.test.(js|jsx|ts|tsx)',
    '<rootDir>/v0/**/*.test.(js|jsx|ts|tsx)',
  ],
  
  // Files to ignore
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/v0/.next/',
    '<rootDir>/v0/node_modules/',
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'v0/components/**/*.{js,jsx,ts,tsx}',
    'v0/hooks/**/*.{js,jsx,ts,tsx}',
    'v0/lib/**/*.{js,jsx,ts,tsx}',
    'v0/pages/**/*.{js,jsx,ts,tsx}',
    '!v0/pages/_app.tsx',
    '!v0/pages/_document.tsx',
    '!v0/pages/api/**',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/.next/**',
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 85,
      statements: 85,
    },
    // Stricter thresholds for critical components
    'v0/components/dashboard/': {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90,
    },
  },
  
  // Coverage reporters
  coverageReporters: [
    'text',
    'lcov',
    'html',
    'json-summary'
  ],
  
  // Coverage directory
  coverageDirectory: '<rootDir>/coverage',
  
  // Transform configuration
  transform: {
    // Use babel-jest to transpile tests with the next/babel preset
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    '/node_modules/',
    '^.+\\.module\\.(css|sass|scss)$',
  ],
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  // Test timeout
  testTimeout: 10000,
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Error on deprecated features
  errorOnDeprecated: true,
  
  // Fail fast on first error in CI
  bail: process.env.CI ? 1 : 0,
  
  // Max workers for parallel test execution
  maxWorkers: process.env.CI ? 2 : '50%',
  
  // Global variables available in tests
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
  
  // Jest extensions
  setupFiles: ['<rootDir>/tests/config/polyfills.js'],
  
  // Custom reporters
  reporters: [
    'default',
    ...(process.env.CI ? [['jest-junit', { outputDirectory: 'test-results' }]] : []),
  ],
  
  // Watch plugins for better DX
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  
  // Snapshot serializers
  snapshotSerializers: ['@emotion/jest/serializer'],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig); 