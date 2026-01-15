# Todo AI Chatbot - Frontend

Next.js frontend for the Todo AI Chatbot, providing a chat interface for natural language task management.

## Prerequisites

- Node.js 18+
- npm or yarn

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

3. Start the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## Features

- Natural language chat interface for task management
- Conversation continuity across sessions
- New conversation button to start fresh
- Tool call visualization in responses
- Loading states and error handling
- Responsive design with Tailwind CSS

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx       # Main chat page
│   │   ├── layout.tsx     # Root layout
│   │   └── globals.css    # Global styles
│   ├── components/
│   │   └── ChatInterface.tsx  # Chat UI component
│   └── lib/
│       └── api.ts         # API client
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Usage Examples

Try these natural language commands:

- "Add a task to buy groceries"
- "Show me my tasks"
- "Show only pending tasks"
- "Mark the groceries task as done"
- "Delete all completed tasks"
- "Rename the task to buy vegetables"
