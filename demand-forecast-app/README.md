# Demand Forecasting Web App

A modern web application built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui for demand forecasting with file upload and data visualization capabilities.

## Features

- 📊 **File Upload**: Support for CSV and Excel files with drag-and-drop functionality
- 📅 **Date Format Detection**: Automatically detects various date formats (DD/MM/YYYY, MM/YYYY, YYYY)
- 📈 **Interactive Charts**: Beautiful forecast visualization with Recharts showing actual vs predicted data
- 📋 **Data Tables**: Detailed forecast results with export functionality
- 🌙 **Dark Mode**: Full dark mode support with system preference detection
- 📱 **Responsive Design**: Mobile-friendly interface that works on all devices
- 🔧 **API Integration**: Configurable API endpoint with mock data fallback
- 📤 **Export Options**: Download charts as PNG and export data as CSV

## Technologies Used

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **File Processing**: PapaParse (CSV), xlsx (Excel)
- **Date Handling**: date-fns
- **Theme**: next-themes
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd demand-forecast-app
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### 1. Upload Data File

- Drag and drop or click to upload a CSV or Excel file
- File must contain at least one date column and one numeric column
- Supported date formats: DD/MM/YYYY, MM/YYYY, YYYY
- Maximum file size: 10MB

### 2. Configure Forecast

- Select your date column from detected date columns
- Choose the demand column (numeric data to forecast)
- Set forecast horizon (1-24 months)

### 3. Generate Forecast

- Click "Generate Forecast" to create predictions
- View interactive chart with confidence intervals
- Export results as CSV or download chart as PNG

### Sample Data

A sample CSV file is included at `public/sample-demand-data.csv` for testing purposes.

## API Configuration

### External API Integration

Set the `MODEL_API_URL` environment variable to integrate with an external forecasting API:

```bash
# .env.local
MODEL_API_URL=https://your-forecast-api.com
```

The API should accept POST requests to `/forecast` with the following format:

**Request:**
```json
{
  "series": [
    { "ds": "2023-01-01", "y": 1200 },
    { "ds": "2023-02-01", "y": 1150 }
  ],
  "horizon": 6,
  "demandColumn": "Demand"
}
```

**Response:**
```json
{
  "forecast": [
    {
      "ds": "2024-01-01",
      "yhat": 1300,
      "yhat_lower": 1200,
      "yhat_upper": 1400
    }
  ]
}
```

### Mock Data Fallback

If no external API is configured, the application uses a built-in mock forecasting algorithm that generates realistic predictions based on historical trends.

## File Format Requirements

### CSV Files
- Must have a header row
- Date column in supported formats
- At least one numeric column for demand data

### Excel Files
- Supports .xlsx and .xls formats
- Uses the first worksheet
- Same requirements as CSV files

### Supported Date Formats
- DD/MM/YYYY (e.g., 15/03/2023)
- MM/YYYY (e.g., 03/2023)
- YYYY (e.g., 2023)
- DD-MM-YYYY (e.g., 15-03-2023)
- MM-YYYY (e.g., 03-2023)
- YYYY-MM-DD (e.g., 2023-03-15)

## Development

### Project Structure

```
src/
├── app/
│   ├── api/forecast/     # API endpoint
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Main page
├── components/
│   ├── ui/              # shadcn/ui components
│   ├── file-upload.tsx  # File upload component
│   ├── forecast-chart.tsx # Chart visualization
│   ├── forecast-table.tsx # Results table
│   ├── mode-toggle.tsx  # Dark mode toggle
│   └── theme-provider.tsx # Theme provider
└── lib/
    ├── data-utils.ts    # Data processing utilities
    └── utils.ts         # Utility functions
```

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
