/// <reference types="@types/jest" />

import React from 'react'
import { render, screen, act, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'

// Component that exposes auth context state for assertions
function AuthDisplay() {
  const { user, token, loading, error, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="loading">{String(loading)}</span>
      <span data-testid="user">{user ? user.email : 'null'}</span>
      <span data-testid="token">{token ?? 'null'}</span>
      <span data-testid="error">{error ?? 'null'}</span>
      <button onClick={() => login('a@b.com', 'pass').catch(() => {})}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  )
}

const renderWithAuth = (ui = <AuthDisplay />) =>
  render(<AuthProvider>{ui}</AuthProvider>)

beforeEach(() => {
  localStorage.clear()
  global.fetch = jest.fn()
})

afterEach(() => {
  jest.resetAllMocks()
})

// ─── Session persistence ─────────────────────────────────────────────────────

describe('session restoration', () => {
  it('restores token and user from localStorage on mount', async () => {
    const user = { id: 'u1', email: 'stored@example.com', name: 'Alice', created_at: '' }
    localStorage.setItem('sentinel_token', 'stored-jwt')
    localStorage.setItem('sentinel_user', JSON.stringify(user))

    renderWithAuth()

    await waitFor(() => {
      expect(screen.getByTestId('token').textContent).toBe('stored-jwt')
      expect(screen.getByTestId('user').textContent).toBe('stored@example.com')
    })
  })

  it('handles corrupted localStorage JSON without crashing', async () => {
    localStorage.setItem('sentinel_token', 'some-token')
    localStorage.setItem('sentinel_user', '{invalid json}')

    renderWithAuth()

    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
      expect(screen.getByTestId('user').textContent).toBe('null')
      expect(localStorage.getItem('sentinel_token')).toBeNull()
    })
  })

  it('starts with no user when localStorage is empty', async () => {
    renderWithAuth()

    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
      expect(screen.getByTestId('user').textContent).toBe('null')
      expect(screen.getByTestId('token').textContent).toBe('null')
    })
  })
})

// ─── login ───────────────────────────────────────────────────────────────────

describe('login', () => {
  it('persists token and user to localStorage on success', async () => {
    const mockUser = { id: 'u2', email: 'login@test.com', name: 'Bob', created_at: '' }
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: 'new-jwt', user: mockUser }),
    })

    renderWithAuth()
    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'))

    await act(async () => {
      screen.getByRole('button', { name: 'login' }).click()
    })

    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('login@test.com')
      expect(screen.getByTestId('token').textContent).toBe('new-jwt')
      expect(localStorage.getItem('sentinel_token')).toBe('new-jwt')
      expect(JSON.parse(localStorage.getItem('sentinel_user')!).email).toBe('login@test.com')
    })
  })

  it('sets error state when login request fails', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Invalid credentials' }),
    })

    renderWithAuth()
    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'))

    await act(async () => {
      screen.getByRole('button', { name: 'login' }).click()
    })

    await waitFor(() => {
      expect(screen.getByTestId('error').textContent).toBe('Invalid credentials')
      expect(screen.getByTestId('user').textContent).toBe('null')
    })
  })
})

// ─── logout ──────────────────────────────────────────────────────────────────

describe('logout', () => {
  it('clears user, token, and localStorage', async () => {
    const user = { id: 'u3', email: 'bye@test.com', name: 'Carol', created_at: '' }
    localStorage.setItem('sentinel_token', 'active-jwt')
    localStorage.setItem('sentinel_user', JSON.stringify(user))

    renderWithAuth()
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('bye@test.com'))

    await act(async () => {
      screen.getByRole('button', { name: 'logout' }).click()
    })

    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('null')
      expect(screen.getByTestId('token').textContent).toBe('null')
      expect(localStorage.getItem('sentinel_token')).toBeNull()
      expect(localStorage.getItem('sentinel_user')).toBeNull()
    })
  })
})

// ─── useAuth guard ───────────────────────────────────────────────────────────

describe('useAuth', () => {
  it('throws when used outside AuthProvider', () => {
    // Suppress expected React error output
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => render(<AuthDisplay />)).toThrow('useAuth must be used within an AuthProvider')
    spy.mockRestore()
  })
})
