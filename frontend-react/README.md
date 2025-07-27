# StockAI React Frontend

A modern, beautiful React frontend for the StockAI application built with Vite, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Beautiful UI**: Modern design with Tailwind CSS and custom components
- 🔐 **Authentication**: Login, registration, and email verification
- 📱 **Responsive**: Mobile-first design that works on all devices
- ⚡ **Fast**: Built with Vite for lightning-fast development
- 🎯 **Accessible**: Proper ARIA labels and keyboard navigation
- 🔍 **Unique IDs**: Every component has unique IDs for easy targeting

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Headless UI** - Accessible UI components
- **Heroicons** - Beautiful SVG icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:3001
   ```

### Environment Variables

Create a `.env` file in the root directory:

```bash
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── auth/           # Authentication components
│   ├── common/         # Reusable UI components
│   └── dashboard/      # Dashboard components
├── pages/              # Page components
├── services/           # API services
├── types/              # TypeScript type definitions
├── App.tsx             # Main app component
└── main.tsx            # App entry point
```

## Component IDs

Every component has unique IDs for easy targeting:

- `login-container` - Main login page container
- `login-form` - Login/registration form
- `email-input` - Email input field
- `password-input` - Password input field
- `submit-button` - Form submit button
- `google-login-button` - Google OAuth button
- `dashboard-page` - Dashboard page container

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Development

### Adding New Components

1. Create component in appropriate directory
2. Add unique ID to root element
3. Import and use in parent component
4. Add TypeScript types if needed

### Styling

- Use Tailwind CSS classes for styling
- Custom components defined in `src/index.css`
- Follow the design system with primary, success, error colors

### API Integration

- All API calls go through `src/services/api.ts`
- Use TypeScript interfaces for type safety
- Handle loading and error states properly

## Migration from Next.js

This React frontend replaces the Next.js version with:

- ✅ **Simpler architecture** - No Next.js complexity
- ✅ **Better UI control** - Direct React components  
- ✅ **Faster development** - Vite hot reload
- ✅ **Smaller bundle** - No Next.js overhead
- ✅ **More flexibility** - Choose any UI library

## Deployment

### Build for Production

```bash
npm run build
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Contributing

1. Follow the existing code style
2. Add unique IDs to all components
3. Use TypeScript for type safety
4. Test on mobile and desktop
5. Ensure accessibility standards

## License

MIT License - see LICENSE file for details
