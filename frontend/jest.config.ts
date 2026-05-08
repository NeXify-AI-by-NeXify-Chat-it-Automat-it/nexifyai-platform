/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterSetup: ['@testing-library/jest-dom'],
  moduleNameMapping: {
    '^@nexifyai/events$': '<rootDir>/../packages/events',
    '^@nexifyai/ui$': '<rootDir>/../packages/ui',
    '\\.(css|scss)$': 'identity-obj-proxy',
    '\\.(png|jpg|svg)$': '<rootDir>/__mocks__/fileMock.ts',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
  ],
  coverageThresholds: {
    global: {
      branches: 70,
      functions: 70,
      lines: 80,
      statements: 80,
    },
  },
  testMatch: ['**/__tests__/**/*.test.{ts,tsx}'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
};
