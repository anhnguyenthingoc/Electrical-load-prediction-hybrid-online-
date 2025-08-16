import { parse, isValid } from 'date-fns';

export interface DataRow {
  [key: string]: string | number | null;
}

export interface ParsedData {
  data: DataRow[];
  columns: string[];
  dateColumn: string | null;
  numericColumns: string[];
}

export interface ForecastSeries {
  ds: string;
  y: number;
}

// Date format patterns to try
const DATE_PATTERNS = [
  'dd/MM/yyyy',
  'MM/yyyy', 
  'yyyy',
  'dd-MM-yyyy',
  'MM-yyyy',
  'yyyy-MM-dd',
  'MM/dd/yyyy',
  'dd.MM.yyyy',
  'MM.yyyy'
];

export function parseDate(dateString: string): Date | null {
  if (!dateString || typeof dateString !== 'string') return null;
  
  const cleanDateString = dateString.trim();
  
  // Try each date pattern
  for (const pattern of DATE_PATTERNS) {
    try {
      const parsed = parse(cleanDateString, pattern, new Date());
      if (isValid(parsed)) {
        return parsed;
      }
    } catch {
      continue;
    }
  }
  
  // Try native Date parsing as fallback
  const nativeDate = new Date(cleanDateString);
  return isValid(nativeDate) ? nativeDate : null;
}

export function isDateColumn(columnData: (string | number | null)[]): boolean {
  if (columnData.length === 0) return false;
  
  let validDates = 0;
  let totalNonEmpty = 0;
  
  for (const value of columnData.slice(0, Math.min(10, columnData.length))) {
    if (value !== null && value !== undefined && value !== '') {
      totalNonEmpty++;
      if (parseDate(String(value))) {
        validDates++;
      }
    }
  }
  
  return totalNonEmpty > 0 && validDates / totalNonEmpty >= 0.8;
}

export function isNumericColumn(columnData: (string | number | null)[]): boolean {
  if (columnData.length === 0) return false;
  
  let numericValues = 0;
  let totalNonEmpty = 0;
  
  for (const value of columnData.slice(0, Math.min(10, columnData.length))) {
    if (value !== null && value !== undefined && value !== '') {
      totalNonEmpty++;
      const numValue = Number(value);
      if (!isNaN(numValue) && isFinite(numValue)) {
        numericValues++;
      }
    }
  }
  
  return totalNonEmpty > 0 && numericValues / totalNonEmpty >= 0.8;
}

export function detectColumnTypes(data: DataRow[]): {
  dateColumns: string[];
  numericColumns: string[];
} {
  if (data.length === 0) {
    return { dateColumns: [], numericColumns: [] };
  }
  
  const columns = Object.keys(data[0]);
  const dateColumns: string[] = [];
  const numericColumns: string[] = [];
  
  for (const column of columns) {
    const columnData = data.map(row => row[column]);
    
    if (isDateColumn(columnData)) {
      dateColumns.push(column);
    } else if (isNumericColumn(columnData)) {
      numericColumns.push(column);
    }
  }
  
  return { dateColumns, numericColumns };
}

export function convertToForecastSeries(
  data: DataRow[],
  dateColumn: string,
  demandColumn: string
): ForecastSeries[] {
  const series: ForecastSeries[] = [];
  
  for (const row of data) {
    const dateValue = row[dateColumn];
    const demandValue = row[demandColumn];
    
    if (dateValue && demandValue !== null && demandValue !== undefined) {
      const parsedDate = parseDate(String(dateValue));
      const numericDemand = Number(demandValue);
      
      if (parsedDate && !isNaN(numericDemand) && isFinite(numericDemand)) {
        series.push({
          ds: parsedDate.toISOString().split('T')[0], // YYYY-MM-DD format
          y: numericDemand
        });
      }
    }
  }
  
  // Sort by date
  return series.sort((a, b) => new Date(a.ds).getTime() - new Date(b.ds).getTime());
}

export function generateMockForecast(
  series: ForecastSeries[],
  horizon: number
): { ds: string; yhat: number; yhat_lower: number; yhat_upper: number }[] {
  if (series.length === 0) return [];
  
  // Simple trend calculation
  const values = series.map(s => s.y);
  const n = values.length;
  const trend = n > 1 ? (values[n-1] - values[0]) / (n-1) : 0;
  const baseValue = values[n-1] || 0;
  const variance = calculateVariance(values);
  
  const forecast = [];
  const lastDate = new Date(series[series.length - 1].ds);
  
  for (let i = 1; i <= horizon; i++) {
    const forecastDate = new Date(lastDate);
    forecastDate.setMonth(forecastDate.getMonth() + i);
    
    const predictedValue = baseValue + (trend * i);
    const uncertainty = Math.sqrt(variance * i) * 1.96; // 95% confidence
    
    forecast.push({
      ds: forecastDate.toISOString().split('T')[0],
      yhat: Math.max(0, predictedValue),
      yhat_lower: Math.max(0, predictedValue - uncertainty),
      yhat_upper: predictedValue + uncertainty
    });
  }
  
  return forecast;
}

function calculateVariance(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
  return squaredDiffs.reduce((a, b) => a + b, 0) / (values.length - 1);
}