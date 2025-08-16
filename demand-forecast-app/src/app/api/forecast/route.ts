import { NextRequest, NextResponse } from 'next/server';
import { ForecastSeries, generateMockForecast } from '@/lib/data-utils';

export interface ForecastRequest {
  series: ForecastSeries[];
  horizon: number;
  demandColumn: string;
}

export interface ForecastResponse {
  forecast: Array<{
    ds: string;
    yhat: number;
    yhat_lower: number;
    yhat_upper: number;
  }>;
}

export async function POST(request: NextRequest) {
  try {
    const body: ForecastRequest = await request.json();
    
    // Validate request
    if (!body.series || !Array.isArray(body.series)) {
      return NextResponse.json(
        { error: 'Invalid series data' },
        { status: 400 }
      );
    }

    if (!body.horizon || body.horizon < 1 || body.horizon > 24) {
      return NextResponse.json(
        { error: 'Horizon must be between 1 and 24 months' },
        { status: 400 }
      );
    }

    if (body.series.length === 0) {
      return NextResponse.json(
        { error: 'Series data cannot be empty' },
        { status: 400 }
      );
    }

    // Check if MODEL_API_URL environment variable exists
    const modelApiUrl = process.env.MODEL_API_URL;
    
    if (modelApiUrl) {
      try {
        // Forward request to external API
        const response = await fetch(`${modelApiUrl}/forecast`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          throw new Error(`External API error: ${response.status}`);
        }

        const forecast: ForecastResponse = await response.json();
        return NextResponse.json(forecast);
      } catch (error) {
        console.error('External API failed, falling back to mock data:', error);
        // Fall through to mock data generation
      }
    }

    // Generate mock forecast data
    const mockForecast = generateMockForecast(body.series, body.horizon);
    
    const response: ForecastResponse = {
      forecast: mockForecast
    };

    return NextResponse.json(response);

  } catch (error) {
    console.error('Forecast API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { 
      message: 'Forecast API is running',
      endpoints: {
        POST: '/api/forecast - Generate demand forecast'
      }
    }
  );
}