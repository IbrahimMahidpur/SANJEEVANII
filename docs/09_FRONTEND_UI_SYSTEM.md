# 🎨 Feature 9: Frontend UI System & Design

## Overview

The SANJEEVANII frontend is built with **React + TypeScript + Vite** and implements a premium, glassmorphic dark-mode UI with custom animations, a multi-page routing system, an animated orb homepage, and a staggered navigation menu.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/App.tsx`](../src/App.tsx) | Root app + React Router setup |
| [`src/index.css`](../src/index.css) | Global styles + custom CSS |
| [`src/pages/Home.tsx`](../src/pages/Home.tsx) | Landing page |
| [`src/pages/Sanjeevani.tsx`](../src/pages/Sanjeevani.tsx) | Sanjeevani info page |
| [`src/components/Orb.tsx`](../src/components/Orb.tsx) | Animated orb background |
| [`src/components/StaggeredMenu.tsx`](../src/components/StaggeredMenu.tsx) | Navigation menu (24KB) |
| [`src/components/PromptBox.tsx`](../src/components/PromptBox.tsx) | Chat input with tool selector |
| [`src/components/Sidebar.tsx`](../src/components/Sidebar.tsx) | Chat sidebar |
| [`src/components/HeatmapModal.tsx`](../src/components/HeatmapModal.tsx) | Fullscreen heatmap modal |
| [`src/components/ThemeToggle.tsx`](../src/components/ThemeToggle.tsx) | Dark/light mode toggle |
| [`vite.config.ts`](../vite.config.ts) | Vite build configuration |
| [`tsconfig.app.json`](../tsconfig.app.json) | TypeScript config |

---

## 🧩 Features

### 1. Animated Orb (`Orb.tsx`)
A mesmerizing animated orb on the homepage:
- Radial gradient glow effect
- CSS keyframe pulse animation
- Acts as the ambient centerpiece of the landing page

### 2. Staggered Navigation Menu (`StaggeredMenu.tsx`)
A full-screen navigation overlay with:
- Staggered entry animations for each menu item
- Blur backdrop
- Links to all major features:
  - AI Health Chat
  - Outbreak Alert System
  - Prescription Analysis
  - Pharmacy Support
  - CBT Voice Therapy (June)
  - Community Forum

### 3. PromptBox Component
Advanced chat input component with:
- **Tool Selector**: Dropdown to choose AI mode (Search, Plan, Think, Research)
- **File Upload**: Image attach for medical image analysis
- **Keyboard shortcuts**: Enter to send, Shift+Enter for newline
- **Character count** and submit button state management

### 4. Sidebar (Chat History)
- Lists previous chat sessions
- "New Chat" button
- Session title auto-generated from first message

### 5. React Router Setup
```tsx
// App.tsx - Route definitions
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/chat" element={<Chat />} />
  <Route path="/outbreak-alerts" element={<OutbreakAlert />} />
  <Route path="/prescription-analysis" element={<PrescriptionAnalysis />} />
  <Route path="/pharmacy-support" element={<PharmacySupport />} />
  <Route path="/community" element={<CommunityForum />} />
  <Route path="/sanjeevani" element={<Sanjeevani />} />
</Routes>
```

### 6. Theme System
- Dark mode by default (`bg-[#212121]`)
- Community Forum supports full dark/light toggle
- `ThemeToggle.tsx` switches CSS class on `<html>`
- Smooth 300ms CSS transitions on all themed elements

### 7. Markdown Rendering
Chat messages render full **GitHub Flavored Markdown**:
```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {messageContent}
</ReactMarkdown>
```

Supports: tables, code blocks, bold/italic, lists, blockquotes, links.

### 8. Thinking Block Collapsible
LLM `<think>...</think>` blocks are parsed and rendered as collapsible sections:
```tsx
msg.content.split(/<think>([\s\S]*?)<\/think>/g).map((part, i) => {
  if (i % 2 === 1) {
    return (
      <details>
        <summary>Thinking Process</summary>
        <div>{part}</div>
      </details>
    );
  }
  return <ReactMarkdown>{part}</ReactMarkdown>;
});
```

### 9. Glassmorphism Design System
Consistent UI tokens used across all pages:
```css
/* Glassmorphic card */
backdrop-blur-xl
bg-gray-900/50
border border-gray-800
rounded-2xl

/* Gradient text */
bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent

/* Ambient orbs */
bg-purple-900/10 rounded-full blur-[120px]
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| Routing | React Router v6 |
| Animation | Framer Motion + CSS keyframes |
| Markdown | react-markdown + remark-gfm |
| Icons | Lucide React |
| Styling | CSS + inline Tailwind utilities |
| Linting | ESLint + TypeScript ESLint |

---

## 🚀 Development

```bash
npm install
npm run dev     # Dev server at http://localhost:5173
npm run build   # Production build
npm run lint    # ESLint check
```

### TypeScript Config
- Target: `ES2020`
- Strict mode enabled
- Path aliases configured in `tsconfig.app.json`
