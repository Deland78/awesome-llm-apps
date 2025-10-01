// Learn more: https://github.com/testing-library/jest-dom
// Only import jest-dom for jsdom environment (not for node environment tests)
if (typeof window !== 'undefined') {
  require('@testing-library/jest-dom')
}

// Mock environment variables
process.env.BACKEND_API_URL = 'http://localhost:8000'
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/test'
