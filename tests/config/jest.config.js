// Jest configuration for Dashboard v4

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Set explicit root directory
  rootDir: '../../',
  
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/config/setup.ts'],
  
  // Module paths
  moduleDirectories: ['node_modules', '<rootDir>/'],
  moduleNameMapper: {
    // Handle module aliases (same as in your Next.js config)
    '^@/components/(.*)$': '<rootDir>/Project Information/v0/components/$1',
    '^@/pages/(.*)$': '<rootDir>/Project Information/v0/pages/$1',
    '^@/lib/(.*)$': '<rootDir>/Project Information/v0/lib/$1',
    '^@/hooks/(.*)$': '<rootDir>/Project Information/v0/hooks/$1',
    '^@/types/(.*)$': '<rootDir>/Project Information/v0/types/$1',
    '^@/styles/(.*)$': '<rootDir>/Project Information/v0/styles/$1',
    '^@/public/(.*)$': '<rootDir>/Project Information/v0/public/$1',
    
    // Handle CSS imports (identity object proxy for CSS modules)
    '^.+\\.(css|sass|scss)$': 'identity-obj-proxy',
    
    // Handle image imports
    '^.+\\.(png|jpg|jpeg|gif|webp|avif|ico|bmp|svg)$': '<rootDir>/tests/__mocks__/file-mock.js',
  },
  
  // Test file patterns
  testMatch: [
    '<rootDir>/tests/unit/**/*.test.(js|jsx|ts|tsx)',
    '<rootDir>/tests/integration/**/*.test.(js|jsx|ts|tsx)',
    '<rootDir>/Project Information/v0/**/*.test.(js|jsx|ts|tsx)',
  ],
  
  // Files to ignore
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/Project Information/v0/.next/',
    '<rootDir>/Project Information/v0/node_modules/',
    '<rootDir>/tests/e2e/',
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'Project Information/v0/components/**/*.{js,jsx,ts,tsx}',
    'Project Information/v0/hooks/**/*.{js,jsx,ts,tsx}',
    'Project Information/v0/lib/**/*.{js,jsx,ts,tsx}',
    'Project Information/v0/pages/**/*.{js,jsx,ts,tsx}',
    '!Project Information/v0/pages/_app.tsx',
    '!Project Information/v0/pages/_document.tsx',
    '!Project Information/v0/pages/api/**',
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
    'Project Information/v0/components/dashboard/': {
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
  
  // Transform configuration - Use babel-jest for all JS/TS files
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    '/node_modules/(?!(some-es6-module)/)',
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
  
  // Jest extensions
  setupFiles: ['<rootDir>/tests/config/polyfills.js'],
  
  // Custom reporters
  reporters: [
    'default',
    ...(process.env.CI ? [['jest-junit', { outputDirectory: 'test-results' }]] : []),
  ],
  
  // Watch plugins for better DX
  watchPlugins: [
    // 'jest-watch-typeahead/filename',
    // 'jest-watch-typeahead/testname',
  ],
  
  // Snapshot serializers
  // snapshotSerializers: ['@emotion/jest/serializer'],
};

module.exports = customJestConfig; 