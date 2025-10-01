/**
 * @jest-environment node
 */
import { POST } from '@/app/api/plan/submit/route'
import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    tripPlan: {
      create: jest.fn(),
    },
  },
}))

// Mock fetch
global.fetch = jest.fn()

describe('POST /api/plan/submit', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  const validTripData = {
    name: 'Paris Adventure',
    destination: 'Paris, France',
    startingLocation: 'New York, USA',
    travelDates: { start: '2025-06-01', end: '2025-06-10' },
    dateInputType: 'picker',
    duration: 9,
    travelingWith: 'partner',
    adults: 2,
    children: 0,
    ageGroups: [],
    budget: 5000,
    budgetCurrency: 'USD',
    travelStyle: 'luxury',
    budgetFlexible: true,
    vibes: ['romantic', 'cultural'],
    priorities: ['attractions', 'food'],
    interests: 'art museums',
    rooms: 1,
    pace: [3],
    beenThereBefore: 'no',
    lovedPlaces: '',
    additionalInfo: 'Looking for authentic experiences',
  }

  it('should successfully submit trip plan', async () => {
    const mockTripPlan = {
      id: 'trip-123',
      ...validTripData,
      travelDatesStart: validTripData.travelDates.start,
      travelDatesEnd: validTripData.travelDates.end,
      userId: null,
    }

    ;(prisma.tripPlan.create as jest.Mock).mockResolvedValue(mockTripPlan)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Travel plan triggered',
        trip_plan_id: 'trip-123',
      }),
    })

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(validTripData),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(data.tripPlanId).toBe('trip-123')
    expect(prisma.tripPlan.create).toHaveBeenCalledTimes(1)
  })

  it('should return 400 for missing required fields', async () => {
    const invalidData = {
      name: 'Trip',
      // Missing destination and startingLocation
    }

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(invalidData),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(400)
    expect(data.success).toBe(false)
    expect(data.message).toContain('Missing required fields')
  })

  it('should handle database errors', async () => {
    ;(prisma.tripPlan.create as jest.Mock).mockRejectedValue(
      new Error('Database error')
    )

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(validTripData),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(500)
    expect(data.success).toBe(false)
    expect(data.message).toContain('Failed to save trip plan')
  })

  it('should handle backend API errors', async () => {
    const mockTripPlan = {
      id: 'trip-123',
      ...validTripData,
      travelDatesStart: validTripData.travelDates.start,
      travelDatesEnd: validTripData.travelDates.end,
      userId: null,
    }

    ;(prisma.tripPlan.create as jest.Mock).mockResolvedValue(mockTripPlan)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      text: async () => 'Backend error',
    })

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(validTripData),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(500)
    expect(data.success).toBe(false)
    expect(data.message).toContain('Failed to trigger trip planning')
  })

  it('should save trip plan to database with correct data', async () => {
    const mockTripPlan = {
      id: 'trip-123',
      ...validTripData,
      travelDatesStart: validTripData.travelDates.start,
      travelDatesEnd: validTripData.travelDates.end,
      userId: null,
    }

    ;(prisma.tripPlan.create as jest.Mock).mockResolvedValue(mockTripPlan)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, trip_plan_id: 'trip-123' }),
    })

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(validTripData),
    })

    await POST(request)

    expect(prisma.tripPlan.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        name: validTripData.name,
        destination: validTripData.destination,
        startingLocation: validTripData.startingLocation,
        adults: validTripData.adults,
        budget: validTripData.budget,
      }),
    })
  })

  it('should call backend API with correct payload', async () => {
    const mockTripPlan = {
      id: 'trip-123',
      ...validTripData,
      travelDatesStart: validTripData.travelDates.start,
      travelDatesEnd: validTripData.travelDates.end,
      userId: null,
    }

    ;(prisma.tripPlan.create as jest.Mock).mockResolvedValue(mockTripPlan)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, trip_plan_id: 'trip-123' }),
    })

    const request = new NextRequest('http://localhost:3000/api/plan/submit', {
      method: 'POST',
      body: JSON.stringify(validTripData),
    })

    await POST(request)

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/plan/trigger'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.any(String),
      })
    )
  })
})
